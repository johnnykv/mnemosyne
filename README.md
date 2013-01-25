Mnemosyne [![Build Status](https://travis-ci.org/johnnykv/mnemosyne.png?branch=master)](https://travis-ci.org/johnnykv/mnemosyne)
=========
## About
Mnemosyne has three main objectives:

1. Provide immutable persistence for [hpfeeds](https://redmine.honeynet.org/projects/hpfeeds/wiki).
2. Normalization of data to enable sensor agnostic analysis.
3. Expose the normalized data through a RESTful API.

## Channels
Mnemosyne currently supports normalization of data from the following channels:

* dionaea.capture
* mwbinary.dionaea.sensorunique
* kippo.sessions
* glastopf.events
* glastopf.files
* thug.events (limited - still under development)

## Preliminary REST API
Can be found at [http://johnnykv.github.com/mnemosyne/WebAPI.html](http://johnnykv.github.com/mnemosyne/WebAPI.html)
