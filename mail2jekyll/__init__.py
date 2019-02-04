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

    print(post)
    markdown = html_to_markdown(body)


SUBJECT_LINE_RE = re.compile('^.* <([^>]+)> ([\w/]+)')


def split_subject_line(subject):
    """Return tuple of (secret, post_dir). Strips out ``re:``, etc.

    >>> split_subject_line('Re: <secret> journal/story/')
    ('secret', 'journal/story/')
    >>> split_subject_line('RE: FWD: FWD: fake news')
    None
    """

    match = re.match(SUBJECT_LINE_RE, subject)
    if match:
        path = os.path.relpath(match.group(2), '/')
        return (match.group(1), path)

    return (None, None)


def blog_config_for_recipient(to_address):
    for c in config['blogs'].values():
        if c['address'] == to_address:
            return c


def html_to_markdown(html):
    # TODO: Make this configurable
    proc = subprocess.Popen([
        'pandoc',
        '-f', 'html-native_spans-native_divs',
        '-t', 'markdown-escaped_line_breaks'
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
