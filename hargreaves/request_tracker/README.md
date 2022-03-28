# How To Analyse/Debug Requests

We are using HAR files:

HTTP Archive (HAR) format files are an industry standard for exchanging information about HTTP requests and HTTP responses. A HAR file's content is JSON formatted, containing browser interactions with a web site.
https://w3c.github.io/web-performance/specs/HAR/Overview.html

# To Record

We are using Firefox Inspect Development Tools to record a HAR file.
(Unfortunately Google Chrome has a long-standing bug which removes response
content once you navigate away from the page)

```
    Open Inspector ("Right-Click Window > Inspect")
	On "Storage" tab
		Clear *.hl.co.uk" Cookies
	On "Network" tab:
	    Click on gear on the right
		Check "Perist Logs"
		On the right, clickon the the dustbin icon to clear logs
	Address Bar: 
		Start user journey with first URL
	....
	[When you are finished with journey]
	Inspect Tools -> Network Tab:
		Click on the gear icon on the right
		Click on the "Save All As HAR"
```


# Markdown Viewer

You may need to install the markdown viewer extension +
configure it to work with local files (https://addons.mozilla.org/en-GB/firefox/addon/markdown-viewer-webext/)

* Save the HAR file in the "session_cache" temporary folder, i.e. "online.hl.co.uk-firefox-login-buy.har"
* Use the har2md.py script to convert it to a markdown file

```
python3 har2md.py ../../session_cache/online.hl.co.uk-firefox-login-buy.har --v
```
* Open the markdown file in the browser

```
* file:///[MY LOCATION]/session_cache/online.hl.co.uk-firefox-login-buy/output.md
```

# Alternative Viewer

Use Google HAR Analyzer: https://toolbox.googleapps.com/apps/har_analyzer/

Some useful filters

```
documents
xhr
```

