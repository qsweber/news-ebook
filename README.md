# News Ebook

Turn your favorite news sources into an ebook for offline,
distraction free reading.

Currently this supports turning the weekly print edition of the Economist
into an HTML document which can then be emailed to your Kindle. You will
need login credentials to economist.com in order to use this.

## Set up

- Clone this repo
- Install it locally (pip install -e /path/to/repo)

## Set up "Economist -> Kindle" sync

There are a few things related to credentials:

- Add your Economist account username and password to a .pass file
- Add your AWS access key and secret key to a .boto file
- Add your to/from email addresses to a .email file

Then simply run this command every Friday:

```economist-kindle```

I set a CRON job on a remote server to run this command for me:

```5 5 * * 5 economist-kindle > /home/ubuntu/news_ebook_logs.txt```
