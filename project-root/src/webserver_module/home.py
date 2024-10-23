from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session, jsonify
)

from webserver_module.auth import login_required
from webserver_module.helpFunctions import clearSessionKeepUser
from main import shutdown_raspi, restart_raspi

from GPIO_module.GPIOs import getDistanceFromSonic, setup_gpio, cleanup_gpio
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

    allData = [{'id': 1, 'name': 'Water Level', 'value': 1}, {'id': 2, 'name': 'Test2', 'value': 2}, {'id': 3, 'name': 'Test3', 'value': 3}, {'id': 4, 'name': 'Test4', 'value': 4}]

    liveData = None
    for data in allData:
        if data['id'] == int(selectedLiveData):
            liveData = data
            break

    if liveData:
        return jsonify(liveData)
    else:
        return 'Error: No data loaded'

def measureDistance(temperatureEnvironment = 24, timeBreak = 0.5, repetitions = 10):
    ultraSonicVelocity_0C = 331300 # mm/s
    ultraSonicVelocity_increase_1C = 600 # mm/s
    sonicVelocity = ultraSonicVelocity_0C + (temperatureEnvironment * ultraSonicVelocity_increase_1C)
    distanceArray = []

    cleanup_gpio()
    setup_gpio()

    for i in range(0, repetitions):
        # Execute the distance measurement via the Raspberry Pi GPIO and the ultrasonic sensor
        # returnPackage = getDistanceFromSonic_high_priority()
        returnPackage = getDistanceFromSonic(sonicVelocity)
        if ['error'] != None:
            distanceArray.append(returnPackage['distance'])
        else:
            flash("Error while measuring the distance: " + returnPackage['error'], 'error')
            return dashBoardViewer()
        # Add the time break to prevent the sensor from being triggered too often
        if timeBreak > 0: # WARNING: Schwebung Möglich --> Störgröße
            time.sleep(timeBreak)
    try:
        print('distanceArray: ', distanceArray)
        # Calculate the average distance
        averageDistance = sum(distanceArray) / len(distanceArray)
        print('averageDistance: ', averageDistance)
        # Delete all runaways, that are not in the range of +- 5mm from the average distance
        distanceArray = [distance for distance in distanceArray if distance > averageDistance - 5 and distance < averageDistance + 5]
        # Calculate the average distance again
        finalDistance = sum(distanceArray) / len(distanceArray)

        # Round the distance
        finalDistance = round(finalDistance, 2)
        print('finalDistance: ', finalDistance)
    except Exception as e:
        flash("Error while calculating the distance: " + str(e), 'error')
        return dashBoardViewer()

    return finalDistance
    
### Enpoint: Set the Zero Water Level Distance ###
@bp.route('/setZeroWaterLevelDistance', methods=('GET', 'POST'))
@login_required
def setZeroWaterLevelDistance():
    temperatureEnvironment = 24
    zeroWaterLevelDistance = measureDistance(temperatureEnvironment)
        
    if zeroWaterLevelDistance:
        try:
            session['zeroWaterLevelDistance'] = float(zeroWaterLevelDistance)
            return jsonify(zeroWaterLevelDistance)
        except:
            flash("Could not set zeroWaterLevelDistance", 'error')
            return dashBoardViewer()
    else:
        flash("Could not set zeroWaterLevelDistance", 'error')
        return dashBoardViewer()    

### Distance Measurement View ###
@bp.route('/measureWaterLevel', methods=('GET', 'POST'))
@login_required
def measureWaterLevel():
    temperatureEnvironment = 24
    distance = measureDistance(temperatureEnvironment)

    # Check if the zeroWaterLevelDistance is set in session, if not use the current distance as zeroWaterLevelDistance
    if 'zeroWaterLevelDistance' not in session:
        try:
            session['zeroWaterLevelDistance'] = float(distance)
        except:
            flash("Could not set zeroWaterLevelDistance", 'error')
            return dashBoardViewer()

    # Calculate the water level based on the zeroWaterLevelDistance
    waterLevel = session['zeroWaterLevelDistance'] - distance
    # waterLevel = distance
    # Round the water level
    waterLevel = round(waterLevel, 2)

    logTextToCSV(str(waterLevel))
    return jsonify(waterLevel)


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
    



    


