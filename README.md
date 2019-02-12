# mail2static

Simple server that receives emails and converts them into content on
static sites.

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

Get the code.

> TODO get this on pypi

Start by copying the example configuration file.

``` console
cp mail2jekyll.{example.,}toml
```

TODO write the rest of it

## todo

- [ ] support IMAP for receiving new email


## license

`mail2static` is available under GNU AGPL 3.0
