import hashlib
import hmac
import json
import tempfile

import flask


page = flask.Blueprint(__name__, __name__)


def create_app(config, queue):
    app = flask.Flask(__name__)

    app.register_blueprint(page)

    app.config['mailgun_api_key'] = config['mailgun']['api_key']
    app.content_queue = queue

    return app


@page.route('/mailgun/message', methods=['POST'])
def receive_mailgun_message():
    req = flask.request

    valid = verify_mailgun_token(
        api_key=flask.current_app.config['mailgun_api_key'],
        timestamp=req.form['timestamp'],
        token=req.form['token'],
        signature=req.form['signature']
    )

    if not valid:
        flask.abort(400)

    data = handle_mailgun_form_data(req.form, req.files)
    flask.current_app.content_queue.put_new_mail(**data)

    return flask.jsonify({})


def handle_mailgun_form_data(form, files):
    body = form['stripped-html']

    content_map = json.loads(form['content-id-map'])
    attachments = write_mailgun_attachments(content_map, files, body)

    return dict(
        sender=form['sender'],
        recipient=form['recipient'],
        subject=form['subject'],
        body=body,
        attachments=attachments
    )


def write_mailgun_attachments(content_map, files, body):
    attachments = {}

    for cid, attachment in content_map.items():
        # <...> -> ...
        cid = cid[1:-1]

        # Skip attachments that aren't actually referenced in this message
        if 'cid:' + cid not in body:
            continue

        _, path = tempfile.mkstemp()
        print(f'created file: {path} for {attachment}')

        upload = files[attachment]
        with open(path, 'wb') as fp:
            fp.write(upload.read())

        attachments[cid] = (path, upload.filename)

    return attachments


def verify_mailgun_token(api_key, timestamp, token, signature):
    digest = hmac.new(
        key=api_key.encode('ascii'),
        msg='{}{}'.format(timestamp, token).encode('ascii'),
        digestmod=hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(
        signature,
        digest
    )
