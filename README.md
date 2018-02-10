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

The app can be deployed to app engine with the `gcloud` App Engine command.

If there are new indexes which need to be generated, run:

```sh
gcloud datastore create-indexes web/index.yaml
```

To deploy the app to App Engine, run:

```sh
gcloud app deploy web
```

## Admin tasks

The admin page allows you to populate the datastore, send emails, and download
the RSVPs. The admin page can be accessed at
[http://karenanderic.com/admin](http://karenanderic.com/admin) but you must be
and admin configured in App Engine.

### Populating the data store

From the admin page, upload the data store by creating the files
`guest_list.csv` and `location_list.csv` and uploading them via the populate
page.

Example `guest_list.csv`:

```csv
invitation_code,first_name,last_name,email,is_child
couple,First1,Last,email1@example.com,0
couple,First2,Last,email2@example.com,0
single,First,Last,email@example.com,0
children,First1,Last,email1@example.com,0
children,First2,Last,email2@example.com,0
children,Child1,Last,email3@example.com,1
children,Child2,Last,email4@example.com,1
plusone,First,Last,email@example.com,0
pluschildren,First,Last,email@example.com,0
cafriend,First,Last,email@example.com,0
cafamily,First,Last,email@example.com,0
hkfriend,First,Last,email@example.com,0
hkfamily,First,Last,email@example.com,0
bothfriend,First,Last,email@example.com,0
bothfamily,First,Last,email@example.com,0
```

Example `location_list.csv`:

```csv
invitation_code,location,has_plus_one,additional_child_count
couple,ca,0,0
single,ca,0,0
children,ca,0,0
plusone,ca,1,0
pluschildren,ca,0,2
cafriend,ca,0,0
cafamily,ca,0,0
cafamily,ca_tc,0,0
hkfriend,hk,0,0
hkfamily,hk,0,0
hkfamily,hk_tc,0,0
bothfriend,ca,0,0
bothfriend,hk,0,0
bothfamily,ca,0,0
bothfamily,ca_tc,0,0
bothfamily,hk,0,0
bothfamily,hk_tc,0,0
```

## Credits & Attributions

### Images

*   [`app/web/static/favicon.ico`](https://www.freefavicon.com/freefavicons/people/iconinfo/wedding-couple-152-182970.html)
*   [`app/web/static/images/event_banner.jpg`](https://pxhere.com/en/photo/489871)
*   Photo Credit [Michael Mak](http://www.michaelmak.co/)
    *   `app/web/static/images/home_banner.jpg`
    *   `app/web/static/images/save_the_date_email.jpg`

### Tools

*   Email layout: [https://mosaico.io](https://mosaico.io)
