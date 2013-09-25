eyeCode Experiment Website
==========================

All files necessary to run the [eyeCode experiment](http://arxiv.org/abs/1304.5257). The experiment consists of a survey, 10 programs, and a post-experiment questionnaire. The site is built on top of [cherrypy](http://www.cherrypy.org/) and [mako](http://www.makotemplates.org/). Data is recorded locally in an [SQLite database](http://www.sqlite.org/) and exported to XML via a Python script.

Requirements (tested with specific versions):

* cherrypy 3.2.2
* sqlalchemy 0.7.8
* mako 0.9.0
* pandas 0.12.0

Running:

* `make serve` - run web server on port 8080
* `make export` - export SQLite database to XML file

Screenshots
-----------

Home screen:

![Home Screen](https://github.com/synesthesiam.com/eyecode-web/raw/master/img/home_screen.png)


Trial screen:

![Trial Screen](https://github.com/synesthesiam.com/eyecode-web/raw/master/img/trial_screen.png)
