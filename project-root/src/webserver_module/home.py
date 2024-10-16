from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session, jsonify
)

from webserver_module.auth import login_required
from webserver_module.helpFunctions import clearSessionKeepUser
from main import shutdown_raspi, restart_raspi

from GPIO_module.GPIOs import getDistanceFromSonic
from Git_module.controlGit import pullFromGit
from saveData_module.saveData import logTextToCSV

import time

bp = Blueprint('home', __name__)


## DASHBOARD VIEWER View ###
@bp.route('/dashBoardViewer', methods=('GET', 'POST'))
@bp.route('/dashBoardViewer/<clearSession>', methods=('GET', 'POST'))
@login_required
def dashBoardViewer(clearSession = False):

    if request.method == 'POST':
        if clearSession == False:
            try:
                if request.form['clearSession'] == 'True' or request.form['clearSession'] == 'true' or request.form['clearSession'] == True:
                    clearSession = True
            except:
                pass

    if clearSession:
        clearSessionKeepUser()

    
    pageTitle = 'Dashboard'
    pageHeaderInfo =  f'Welcome {g.user["name"]} to the Raspberry Pi Interface'
    liveDataHeader = [1, 2, 3, 4]

    return render_template('dashBoard.html', pageTitle=pageTitle, pageHeaderInfo=pageHeaderInfo,  liveDataHeaderJSON=liveDataHeader)


# Endpoint for live loading data base entries via ajax request
@bp.route('/getLiveData', methods=('GET', 'POST'))
@bp.route('/getLiveData/<selectedLiveData>', methods=('GET', 'POST'))
@login_required
def getLiveData(selectedLiveData = None):      
    if request.method == 'POST':
        if selectedLiveData is None:
            try:
                if request.form['selectedLiveData'] == None:
                    selectedLiveData = 1
                else:
                    selectedLiveData = request.form['selectedLiveData']
            except:
                pass    

    allData = [{'id': 1, 'name': 'Distance Measurement', 'value': 1}, {'id': 2, 'name': 'Test2', 'value': 2}, {'id': 3, 'name': 'Test3', 'value': 3}, {'id': 4, 'name': 'Test4', 'value': 4}]

    liveData = None
    for data in allData:
        if data['id'] == int(selectedLiveData):
            liveData = data
            break

    if liveData:
        return jsonify(liveData)
    else:
        return 'Error: No data loaded'
    

### Distance Measurement View ###
@bp.route('/distanceMeasurement', methods=('GET', 'POST'))
@login_required
def distanceMeasurement(timeBreak = 0.05, repetitions = 20):
    if request.method == 'POST':
        try:
            if request.form['timeBreak'] != '':
                timeBreak = request.form['timeBreak']
        except:
            pass
    if request.method == 'POST':
        try:
            if request.form['repetitions'] != '':
                repetitions = request.form['repetitions']
        except:
            pass

    #Convert timeBreak to float
    try:
        timeBreak = float(timeBreak)
    except:
        timeBreak = 0.05

    # Convert repetitions to int
    try:
        repetitions = int(repetitions)
    except:
        repetitions = 10

    distanceSum = 0
    for i in range(0, repetitions):
        # Execute the distance measurement via the Raspberry Pi GPIO and the ultrasonic sensor
        returnPackage = getDistanceFromSonic()
        if returnPackage['error'] != None:
            flash(returnPackage['error'])  
            return dashBoardViewer()
        else:
            distanceSum += returnPackage['data']
        # Add the time break to prevent the sensor from being triggered too often
        if timeBreak > 0:
            time.sleep(timeBreak)
    
    # Calculate the average distance
    distance = distanceSum / repetitions
    # Round the distance
    distance = round(distance, 2)

    logTextToCSV('Distance: ' + str(distance) + ' mm')
    return jsonify(distance)


### Git Sync View ###
@bp.route('/syncGit', methods=('GET', 'POST'))
@bp.route('/syncGit/<branchName>', methods=('GET', 'POST'))
@login_required
def syncGit(branchName = 'main'):
    if request.method == 'POST':
        try:
            if request.form['branchName'] != '':
                branchName = request.form['branchName']
        except:
            pass

    returnPackage = pullFromGit(branchName)

    if returnPackage['error'] != None:
        flash(returnPackage['error'])  
        return dashBoardViewer() 
    else:
        return restartServer()


### Shut down View ###
# --> Shutdown the raspberry pi via its website
@bp.route('/shutdown', methods=('GET', 'POST'))
def shutdown():
    error = shutdown_raspi()
    if error:
        flash(error)
    return dashBoardViewer()
    
    
### Restart Server View ###
@bp.route('/restartServer', methods=('GET', 'POST'))
@login_required
def restartServer():
    error = restart_raspi()
    if error:
        flash(error)
    return dashBoardViewer()
    

# ### Kill Server and main.py View ###
# @bp.route('/killServer', methods=('GET', 'POST'))
# @login_required
# def killServer():
#     error = kill_server()
#     if error:
#         flash(error)
#     return dashBoardViewer()
    



    


