# mail2static

Simple server that receives emails and converts them into content for
static site generators.

For example, set this up to allow you to post to your Jekyll blog
without being near a laptop.

## setup

You will need:

1. Somewhere to run the server. Free tier Heroku or something
   similarly tiny should be fine.
2. A developer account on [mailgun](https://mailgun.com).
3. A static site ready for content. I've tried this with Jekyll, but
   there's no reason you can't use any other thing that accepts
   Markdown content.

Get the code, and set up your environment.

``` console
git clone git@github.com:erik/mail2static.git
python3 -m venv ve && source ve/bin/activate
python setup.py install
```

Start by copying the example configuration file.

``` console
cp mail2static.{example.,}toml
```

Look at the example configuration file for descriptions of what each
key does.

TODO write documentation for this.

Once everything is running, send an email to your configured
`inbox_address` and make sure it works.

```
From: Foo Bar <user@example.org>
Subject: <MY_SUPER_SECRET_VALUE> post/directory/to/use
To: my-inbox-address@somesite.com


Title of the post

Content of the post...
```



## todo

- [ ] support IMAP for receiving new email
- [ ] get this on pypi
- [ ] write some basic documentation

## license

`mail2static` is available under GNU AGPL 3.0
