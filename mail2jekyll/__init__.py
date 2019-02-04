import datetime as dt
import os
import os.path
import json
import re
import subprocess
import tempfile

import flask
import toml

app = flask.Flask(__name__)


def run_debug(config):
    app.debug = True
    app.run(**config)


@app.route('/mailgun/message', methods=['POST'])
def receive_mailgun_message():
    req = flask.request

    # TODO: verify mailgun token
    token = req.form['token']

    sender = req.form['sender']
    recipient = req.form['recipient']
    subject = req.form['subject']

    body_html = req.form['stripped-html']

    attachments = {}
    content_map = json.loads(req.form['content-id-map'])

    for cid, attachment in content_map.items():
        # <...> -> ...
        cid = cid[1:-1]

        # Skip attachments that aren't actually referenced in this message
        if 'cid:' + cid not in body_html:
            continue

        _, path = tempfile.mkstemp()
        print('created file: ' + path)
        with open(path, 'wb') as fp:
            fp.write(req.files[attachment].read())
        attachments[cid] = path

    # TODO: call celery or something instead
    receive_mail(sender, recipient, subject, body_html, attachments)

    return 'ok'


def receive_mail(sender, to, subject, body, files):
    print(f'''
    from={sender}
    to={to}
    subject={subject}
    body={body}
    files={files}
    ''')

    blog_config = blog_config_for_recipient(to)
    if not blog_config:
        print(f'no configuration for recipient: {to}')
        return

    (secret, post_dir) = split_subject_line(subject)
    if secret != blog_config['secret']:
        print(f'bad secret: {secret}')
        return

    markdown = html_to_markdown(body)
    (title, body) = split_post_content(markdown)

    print(f'''
    title => {title}
    markdown => {body}
    files => {files}
    ''')

    write_blog_post(blog_config, post_dir, title, body, files)


def move_asset(asset_path, cid, path):
    renamed = os.path.join(asset_path, cid)

    print(f'moving {path} -> {renamed}')
    os.rename(path, renamed)

    return renamed


def write_blog_post(blog_config, post_dir, title, body, files):
    post_file = generate_post_name(title)

    base_path = os.path.join(
        config['git']['clone_dir'],
        blog_config['directory'])

    assets_path = os.path.join(base_path, blog_config['asset_path'])
    posts_path = os.path.join(base_path, blog_config['post_path'], post_dir)

    os.makedirs(assets_path, exist_ok=True)
    os.makedirs(posts_path, exist_ok=True)

    for cid, path in files.items():
        asset_url = os.path.join('/', blog_config['asset_path'], cid)
        move_asset(assets_path, cid, path)

        body = body.replace(f'cid:{cid}', asset_url)

    post_path = os.path.join(posts_path, post_file)

    with open(post_path, 'w') as fp:
        fp.write(blog_config['post_template'].format(
            content=body,
            title=title
        ))


SUBJECT_LINE_RE = re.compile(r'^.* <([^>]+)> ([\w/]+)')


def split_subject_line(subject):
    """Return tuple of (secret, post_dir). Strips out ``re:``, etc.

    >>> split_subject_line('Re: <secret> journal/story/')
    ('secret', 'journal/story/')
    >>> split_subject_line('RE: FWD: FWD: fake news')
    None
    """

    match = re.match(SUBJECT_LINE_RE, subject)
    if match:
        path = os.path.normpath('/' + match.group(2))[1:]
        return (match.group(1), path)

    return (None, None)


def blog_config_for_recipient(to_address):
    for c in config['blogs'].values():
        if c['address'] == to_address:
            return c


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


def load_configuration(file_name):
    file_name = os.path.expanduser(file_name)
    with open(file_name, 'r') as fp:
        return toml.load(fp)


if __name__ == '__main__':
    config_file = os.environ.get(
        'MAIL2JEKYLL_CONFIG',
        './mail2jekyll.toml'
    )

    config = load_configuration(config_file)
    run_debug(config.get('http', {}))
