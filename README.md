# A Simple Video Streaming Site

A basic video streaming site build with Flask, Plyr, and Dash.js


## TODO

* Move flask app to a subdir
* ADD LOGGING
* Handle duplicate file names during upload
* PEP8 formatting
* Make dev environment with reloading on flaskapp + static resources
* Get Plyr/Dash dependencies from diff CDN/no CDN?
* Minification (necessary?)
* Add linting/format to PEP8 (linting for imports)
* mypy
* Configure a PyCharm workspace
* Use POSIX message queues for transcoding jobs
* Add volumes to Docker compose
* Surface media, upload volumes to Flask via environment variables  
* Postgres/db other than sqlite
* Testing
* Polyfill? Do I care about supporting older browsers?