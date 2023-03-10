#Developers: Federico De Rocco, Tommaso Bertelli

from __future__ import print_function

import sys
import datetime
import json
from TrainMonitor import viaggiatreno

api=viaggiatreno.API()

delayMargin=5
delaySafe=1


def getTrainStatus(trainID):
	departures = api.call("cercaNumeroTrenoTrenoAutocomplete", trainID)
	if len(departures)==0:
		return None
	return api.call("andamentoTreno", departures[0][1], trainID, departures[0][2])

def checkTrain(trainID, stationFullID):
	apiReport=getTrainStatus(trainID)
	if apiReport==None:
		return None
	trainTime=dict()
	trainTime["trainID"]=trainID

	if apiReport['tipoTreno'] == 'ST' or apiReport['provvedimento'] == 1: #train is cancelled
		trainTime["error"]="Cancelled"

	if apiReport["oraUltimoRilevamento"] == None:	#train is not departed yet
		trainTime["error"]="Not departed"

	
	for i in range(len(apiReport["fermate"])): #gets position of the station in the list
		if apiReport["fermate"][i]["id"] == stationFullID:
			break


	trainTime["lastStation"]=apiReport["stazioneUltimoRilevamento"]
	trainTime["tsLastStation"]=apiReport["oraUltimoRilevamento"]
	trainTime["delay"]=apiReport["ritardo"]
	if apiReport["ritardo"]>=delayMargin:
		trainTime["expectedStation"]=apiReport["fermate"][i]["partenza_teorica"]+(apiReport["ritardo"]-delaySafe)*60*1000
	else:
		trainTime["expectedStation"]=apiReport["fermate"][i]["partenza_teorica"]

	return trainTime
	
def checkTrainList(trains, stationFullID):
	listTrainTime=[]
	for x in trains:
		train=checkTrain(x, stationFullID)
		if train != None:
			listTrainTime.append(train)
	return listTrainTime

def filterTrainList(trains, ts):
	for x in trains:
		if x["expectedStation"] != None:
			if int(x["expectedStation"]/1000)+x["delay"]*60<int(ts):
				trains.remove(x)
	return trains
