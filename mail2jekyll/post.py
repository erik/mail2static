import datetime as dt
import os
import os.path
import json
import re
import subprocess
import tempfile


# TODO: Make this celery-based or remove complexity.
# maybe a threadpool even
#
# TODO: also weird that the content queue owns the config
class ContentQueue:
    def __init__(self, config):
        self._config = config
        self._site_configs = {
            c['inbox_address']: c
            for c in config.get('sites', []).values()
        }

    def site_config_for_recipient(self, recipient):
        return self._site_configs[recipient]

    def put_new_mail(self, sender, recipient, subject, body, attachments):
        print(f''' put_new_mail =>
    from={sender}
    to={recipient}
    subject={subject}
    body={body}
    files={attachments}
        ''')

        # TODO: need to hold lock on git

        handle_new_mail(
            self.site_config_for_recipient(recipient),
            sender,
            subject,
            body,
            attachments
        )


def handle_new_mail(config, sender, subject, body, attachments):
    approved_senders = config['approved_senders']
    if approved_senders and sender not in approved_senders:
        print(f'{sender} is not in whitelist: {approved_senders}')
        return

    base_path = config['directory']

    (secret, post_dir) = split_subject_line(subject)
    if secret != config['secret']:
        print(f'bad secret: {secret}')
        return

    body = rewrite_asset_locations(config, base_path, body, attachments)

    markdown = html_to_markdown(body)
    (title, body) = split_post_content(markdown)

    print(f'''
    title => {title}
    markdown => {body}
    files => {attachments}
    ''')

    write_post(config, base_path, post_dir, title, body)


def rewrite_asset_locations(config, base_path, body, attachments):
    assets_path = os.path.join(base_path, config['asset_base_path'])
    os.makedirs(assets_path, exist_ok=True)

    for cid, (temp_path, name) in attachments.items():
        # TODO: need to sanitize name here.
        new_path = os.path.join(assets_path, name)
        os.rename(temp_path, new_path)

        print(f'rename {temp_path} -> {new_path}')

        asset_url = os.path.join('/', config['asset_base_url'], name)
        body = body.replace(f'cid:{cid}', asset_url)

    return body


def write_post(config, base_path, post_dir, title, body):
    # TODO: need to sanitize name here.
    post_file = generate_post_name(title)

    posts_path = os.path.join(
        base_path,
        config['post_base_path'],
        post_dir
    )

    os.makedirs(posts_path, exist_ok=True)

    post_path = os.path.join(posts_path, post_file)

    with open(post_path, 'w') as fp:
        fp.write(config['post_template'].format(
            content=body,
            title=title
        ))


SUBJECT_LINE_RE = re.compile(r'^.*?<([^>]+)> ([\w/]+)')


def split_subject_line(subject):
    """Return tuple of (secret, post_dir). Strips out ``re:``, etc.

    >>> split_subject_line('Re: <secret> journal/story/')
    ('secret', 'journal/story/')
    >>> split_subject_line('RE: FWD: FWD: fake news')
    (None, None)
    """

    match = re.match(SUBJECT_LINE_RE, subject)
    if match:
        path = os.path.normpath('/' + match.group(2))[1:]
        return (match.group(1), path)

    return (None, None)


def split_post_content(markdown):
    """Take the first non-empty line of the post as the title."""
    lines = markdown.splitlines()
    title_line = None

    for i, line in enumerate(lines):
        if line.strip() != '':
            title_line = i
            break

    if title_line is None:
        return ('untitled', '\n'.join(lines))

    return (lines[title_line], '\n'.join(lines[title_line+1:]))


TITLE_POST_RE = re.compile(r'[^\w]')


# TODO: this should be configurable
def generate_post_name(title):
    date = dt.datetime.now().strftime('%Y-%m-%d')
    title = re.sub(TITLE_POST_RE, '_', title)
    return f'{date}-{title}.md'


def html_to_markdown(html):
    # TODO: Make this configurable
    proc = subprocess.Popen([
        'pandoc',
        '-f', 'html-native_spans-native_divs',
        '-t', 'markdown-escaped_line_breaks-all_symbols_escapable-header_attributes-auto_identifiers-link_attributes'
    ], stdout=subprocess.PIPE, stdin=subprocess.PIPE)

    out, err = proc.communicate(html.encode('ascii'))
    if err:
        raise Exception(err)

    return out.decode('utf-8')
