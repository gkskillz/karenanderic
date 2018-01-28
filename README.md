# KarenAndEric.com

The source code for the [karenanderic.com](https://karenanderic.com) wedding
website.

## Environment

In order to run the app, you'll need to setup the environment. This includes
creating a secret key used by the session key. The session key file should be
located at `web/session_key.txt` and should not be checked into source. To
generate the key run the command:

```sh
python generate_session_key.py
```

## Local Development

Running the app for local development can be done with the `dev_appserver.py`
App Engine command. Run:

```sh
./dev_appserver.py web
```

## Deployment

The app can be deployed to app engine with the `gcloud` App Engine command. Run:

```sh
gcloud app deploy web
```

## Credits & Attributions

### Images

*   [`app/web/static/favicon.ico`](https://www.freefavicon.com/freefavicons/people/iconinfo/wedding-couple-152-182970.html)
*   [`app/web/static/images/event_banner.jpg`](https://pxhere.com/en/photo/489871)
*   `app/web/static/images/home_banner.jpg`: Photo Credit [Michael Mak](http://www.michaelmak.co/)
