#!flask/bin/python
# -*- coding: UTF-8 -*-

import os
from flask import Flask, render_template, url_for, redirect, abort, json, request, jsonify
import requests, json
from . import app

@app.route('/health/check', methods=['GET'])
def health_check_handler():
    data={}
    data['health'] = 'ok'
    return json.dumps(data)