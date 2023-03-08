from common import D4
from common import D6
from common import D8
from common import D10
from common import D12
from common import D20
from common import D100
from common import random
from dice import diceRoll
from guild import GuildMaker
import json
import os

class ContractMaker:

	dice = diceRoll()
	contratJson = json.loads("{}")

	_MAX_NUMBER_OF_CLAUSES 				= 10
	_MAX_NUMBER_OF_PRE_REQUIREMENTS 	= 10
	_MAX_NUMBER_OF_OBJECTIVES			= 10

	def creatContract(self, guildJson):
		self.guildJson = guildJson

		self.contratJson["guild"] = guildJson #guildJson["name"]

		self.defDueDate			()
		self.defDifficulty		()
		self.defDistance		()
		self.defValeuReward		()
		self.defPreRequirements	()
		self.defClause			()
		self.updateReward		()		#not implemented
		self.defContractor		()
		self.defContractType	()
		self.defObjective		()

		contractPath = "generatedGuild/" + self.guildJson["fileName"] + "/contracts/"
		try:
			os.mkdir(contractPath)
		except:
			print("[ContractMaker] ERROR when creating the folder to the contract returning without the guild")
			#return "error"

		contractNumber = len(os.listdir(contractPath))
		self.contratJson["fileName"] = "contract-" + str(contractNumber) + ".json"
		contractPath = contractPath + "contract-" + str(contractNumber) + ".json"

		with open(contractPath, "w+") as f:
			f.write (json.dumps(self.contratJson, indent=4))
			f.close()

		return self.contratJson
	
	def rollDice (self, diceData):
		diceResult = 0
		print ("[ContractRollDice] Rolling " + str(diceData["diceAmount"]) + "d" + str(diceData["diceType"]) + "+" + str(diceData["diceBonus"]))
		diceResult += self.dice.roll(diceData["diceAmount"], diceData["diceType"])
		diceResult += diceData["diceBonus"] # sede matriz influencia aqui?
		print ("[ContractRollDice] Dice Result = " + str(diceResult))

		return diceResult

	def defDueDate(self):
		f = open("json4Names/ContractServiceValueReward/dueDate.json")
		data = json.load(f)

		diceResult = self.dice.roll(1, 20)

		for i in data:
			if diceResult in range(data[str(i)]["diceRangeMin"], data[str(i)]["diceRangeMax"]+1):
				self.contratJson["dueDate"] = data[str(i)]
				self.contratJson["dueDate"]["rolledDice"] = diceResult
		
		diceResult = 0
		diceResult = self.rollDice(self.contratJson["dueDate"]["amount"]["dueDateDice"])
		diceResult *= int(self.contratJson["dueDate"]["amount"]["diceMultiplier"])

		self.contratJson["dueDate"]["amount"]["value"] += diceResult

		f.close()
		pass
	
	def defDifficulty(self):
		f = open("json4Names/ContractServiceValueReward/contractDistance.json")
		data = json.load(f)

		diceResult = self.rollDice(self.guildJson["size"]["contractDistanceDice"])

		for i in data:
			if diceResult in range(data[str(i)]["diceRangeMin"], data[str(i)]["diceRangeMax"]+1):
				self.contratJson["distance"] = data[str(i)]
				self.contratJson["distance"]["rolledDice"] = diceResult

		f.close()
		pass

	def defDistance(self):
		f = open("json4Names/ContractServiceValueReward/contractDifficulty.json")
		data = json.load(f)

		diceResult = self.dice.roll(1, 20)

		for i in data:
			if diceResult in range(data[str(i)]["diceRangeMin"], data[str(i)]["diceRangeMax"]+1):
				self.contratJson["difficulty"] = data[str(i)]
				self.contratJson["difficulty"]["rolledDice"] = diceResult

		f.close()
		pass

	def defValeuReward(self):
		f = open("json4Names/ContractServiceValueReward/valueReward.json")
		data = json.load(f)

		diceResult = self.dice.roll(1,100)
		diceResultValue 	= diceResult
		diceResultReward 	= diceResult

		#modificadores do resultado do dado

		#area proxima deve influencia no contrato mas nao sei como fazer aqui

		diceResultValue		+= self.contratJson["distance"]["valueRewardModifier"]
		diceResultReward 	+= self.contratJson["distance"]["valueRewardModifier"]
		
		diceResultValue		+= self.guildJson["reputation"]["govern"]["rewardModifier"]["valeuMod"]
		diceResultReward	+= self.guildJson["reputation"]["govern"]["rewardModifier"]["rewardMod"]

		diceResultValue		+= self.guildJson["reputation"]["population"]["rewardModifier"]["valeuMod"]
		diceResultReward	+= self.guildJson["reputation"]["population"]["rewardModifier"]["rewardMod"]

		diceResultValue		+= self.guildJson["employees"]["rewardModifier"]["valeuMod"]
		diceResultReward 	+= self.guildJson["employees"]["rewardModifier"]["rewardMod"]

		if diceResultReward > 100:
			diceResultReward = 100
		elif diceResultReward < 1:
			diceResultReward = 1

		if diceResultValue > 100:
			diceResultValue = 100
		elif diceResultValue < 1:
			diceResultValue = 1

		for i in data:
			if diceResultReward in range(data[str(i)]["diceRangeMin"], data[str(i)]["diceRangeMax"]+1):
				self.contratJson["reward"] = data[str(i)]
				self.contratJson["reward"]["rolledDice"] = diceResultReward
			if diceResultValue in range(data[str(i)]["diceRangeMin"], data[str(i)]["diceRangeMax"]+1):
				self.contratJson["value"] = data[str(i)]
				self.contratJson["value"]["rolledDice"] = diceResultValue

		f.close()
		pass
	
	def defPreRequirements(self):
		f = open("json4Names/ContractServiceValueReward/preRequirementsClause.json")
		data = json.load(f)

		for i in data["diceDefinition"]:
			if self.contratJson["value"]["rolledDice"] in range(data["diceDefinition"][str(i)]["diceRangeMin"], data["diceDefinition"][str(i)]["diceRangeMax"]+1):
				self.contratJson["preRequirementClauseDice"] = data["diceDefinition"][str(i)]

		preRequimentAmount = 1
		preRequimentNumber = 1

		self.contratJson["preRequirement"] = json.loads("{}")

		while preRequimentAmount > 0:
			diceResult = self.rollDice(self.contratJson["preRequirementClauseDice"]["dice"])
			if diceResult < 1:
				diceResult = 1

			for i in data["preRequirements"]:
				if diceResult in range(data["preRequirements"][str(i)]["diceRangeMin"], data["preRequirements"][str(i)]["diceRangeMax"]+1):
					self.contratJson["preRequirement"][str(preRequimentNumber)] = data["preRequirements"][str(i)]
					self.contratJson["preRequirement"][str(preRequimentNumber)]["valueUsed"] = self.contratJson["value"]["rolledDice"]
					self.contratJson["preRequirement"][str(preRequimentNumber)]["rolledDice"] = diceResult
			
			preRequimentAmount -= 1
			preRequimentNumber += 1
			

			#TODO verificar um jeito que nao fique tao hardcoded
			if diceResult in range(data["preRequirements"]["21+"]["diceRangeMin"], data["preRequirements"]["21+"]["diceRangeMax"]+1):
				preRequimentAmount += 2

			if preRequimentNumber > self._MAX_NUMBER_OF_PRE_REQUIREMENTS:
				break

		self.contratJson["preRequirement"]["amount"] = preRequimentNumber - 1

		f.close()
		pass

	def defClause(self):
		f = open("json4Names/ContractServiceValueReward/preRequirementsClause.json")
		data = json.load(f)

		for i in data["diceDefinition"]:
			if self.contratJson["value"]["rolledDice"] in range(data["diceDefinition"][str(i)]["diceRangeMin"], data["diceDefinition"][str(i)]["diceRangeMax"]+1):
				self.contratJson["preRequirementClauseDice"] = data["diceDefinition"][str(i)]

		clauseAmount = 1
		clauseNumber = 1

		self.contratJson["clause"] = json.loads("{}")

		self.contratJson["clause"]["rolledDice"] = json.loads("{}")
		while clauseAmount > 0:
			diceResult = self.rollDice(self.contratJson["preRequirementClauseDice"]["dice"])
			if diceResult < 1:
				diceResult = 1
			for i in data["clause"]:
				if diceResult in range(data["clause"][str(i)]["diceRangeMin"], data["clause"][str(i)]["diceRangeMax"]+1):
					self.contratJson["clause"][str(clauseNumber)] = data["clause"][str(i)]
					self.contratJson["clause"][str(clauseNumber)]["valueUsed"] = self.contratJson["value"]["rolledDice"]
					self.contratJson["clause"][str(clauseNumber)]["rolledDice"] = diceResult
			self.contratJson["clause"]["rolledDice"][str(clauseNumber)] = diceResult
			clauseAmount -= 1
			clauseNumber += 1

			#TODO verificar um jeito que nao fique tao hardcoded
			if diceResult in range(data["clause"]["21+"]["diceRangeMin"], data["clause"]["21+"]["diceRangeMax"]+1):
				clauseAmount += 2

			if clauseNumber > self._MAX_NUMBER_OF_CLAUSES:
				break

		self.contratJson["clause"]["amount"] = clauseNumber - 1

		f.close()
		pass

	def updateReward(self):

		f = open("json4Names/ContractServiceValueReward/valueReward.json")
		data = json.load(f)

		diceResultReward 	= self.contratJson["reward"]["rolledDice"] 

		diceResultReward += 5* ( self.contratJson["clause"]["amount"] + self.contratJson["preRequirement"]["amount"] )

		if diceResultReward > 100:
			diceResultReward = 100
		elif diceResultReward < 1:
			diceResultReward = 1

		for i in data:
			if diceResultReward in range(data[str(i)]["diceRangeMin"], data[str(i)]["diceRangeMax"]+1):
				self.contratJson["reward"] = data[str(i)]
				self.contratJson["reward"]["rolledDice"] = diceResultReward

		self.contratJson["reward"]["totalAmount"] 	= self.contratJson["reward"]["totalAmount"]*self.contratJson["difficulty"]["rewardMultiplier"]
		self.contratJson["value"]["totalAmount"] 	= self.contratJson["value"]["totalAmount"]*self.contratJson["difficulty"]["valueMultiplier"]

		self.contratJson["reward"]["totalAmount"] 	= int(self.contratJson["reward"]["totalAmount"])
		self.contratJson["value"]["totalAmount"]	= int(self.contratJson["value"]["totalAmount"])
		pass

	def defContractor(self):
		f = open("json4Names/ContractServiceValueReward/contractors.json")
		data = json.load(f)

		#TODO 
		diceResult = self.dice.roll(1, 20)
		diceResult += self.guildJson["reputation"]["govern"]["contractorModifier"]
		diceResult += self.guildJson["reputation"]["population"]["contractorModifier"]
		if diceResult <= 0:
			diceResult = 1

		for i in data["who"]:
			if diceResult in range(data["who"][str(i)]["diceRangeMin"], data["who"][str(i)]["diceRangeMax"]+1):
				self.contratJson["contractors"] = data["who"][str(i)]
				self.contratJson["contractors"]["rolledDice"] = diceResult

		if self.contratJson["contractors"]["hasSubClass"] == True:
			subClassData = data[str(self.contratJson["contractors"]["subClassName"])]
			diceResult = self.dice.roll(1, 20)
			for i in subClassData:
				if diceResult in range(subClassData[str(i)]["diceRangeMin"], subClassData[str(i)]["diceRangeMax"]+1):
					self.contratJson["contractors"]["subClass"] = subClassData[str(i)]
					self.contratJson["contractors"]["subClass"]["rolledDice"] = diceResult

		f.close()
		pass

	def defContractType(self):
		f = open("json4Names/ContractServiceValueReward/contractors.json")
		data = json.load(f)

		diceResult = self.dice.roll(1, 20)

		for i in data["contractType"]:
			if diceResult in range(data["contractType"][str(i)]["diceRangeMin"], data["contractType"][str(i)]["diceRangeMax"]+1):
				self.contratJson["contractType"] = data["contractType"][str(i)]
				self.contratJson["contractType"]["rolledDice"] = diceResult

		f.close()
		pass

	def defObjective(self):
		f = open("json4Names/ContractServiceValueReward/objectives.json")
		fullData = json.load(f)
		objectiveJson = json.loads("{\"generalObjectives\": {}}")

		objectiveAmount = 1
		objectiveNumber = 1

		data = fullData["generalObjectives"]
		while objectiveAmount > 0:
			diceResult =  self.dice.roll(1, 20)

			for i in data:
				if diceResult in range(data[str(i)]["diceRangeMin"], data[str(i)]["diceRangeMax"]+1):
					objectiveJson["generalObjectives"][str(objectiveNumber)] = data[str(i)]
					objectiveJson["generalObjectives"][str(objectiveNumber)]["rolledDice"] = diceResult

			#TODO verificar um jeito que nao fique tao hardcoded
			if diceResult in range(data["20+"]["diceRangeMin"], data["20+"]["diceRangeMax"]+1):
				objectiveAmount += 2
			else:
				if objectiveJson["generalObjectives"][str(objectiveNumber)]["objectiveKey"] not in objectiveJson:
					objectiveJson[objectiveJson["generalObjectives"][str(objectiveNumber)]["objectiveKey"]] = json.loads("{}")
					
				objectiveJson[objectiveJson["generalObjectives"][str(objectiveNumber)]["objectiveKey"]][objectiveNumber] = 	\
					self.rollSubObjective (																					\
					fullData[objectiveJson["generalObjectives"][str(objectiveNumber)]["objectiveKey"]])

			objectiveAmount -= 1
			objectiveNumber += 1

			if objectiveNumber > self._MAX_NUMBER_OF_OBJECTIVES:
				break

		self.contratJson["objective"] = objectiveJson
		self.contratJson["objective"]["amount"] = objectiveNumber - 1

		f.close()
		pass

	def rollSubObjective(self, dataJson):
		subObjectiveJson = json.loads("{}")
		diceResult = self.dice.roll(1, 10)

		for i in dataJson:
			if diceResult in range(dataJson[str(i)]["diceRangeMin"], dataJson[str(i)]["diceRangeMax"]+1):
				subObjectiveJson = dataJson[str(i)]
				subObjectiveJson["rolledDice"] = diceResult
		
		if subObjectiveJson["needLocation"] == True:
			f = open("json4Names/ContractServiceValueReward/objectives.json")
			fullData = json.load(f)
			locationJson = fullData["locationOfObjective"]
			diceResult = self.dice.roll(1, 10)

			for i in locationJson:
				if diceResult in range(locationJson[str(i)]["diceRangeMin"], locationJson[str(i)]["diceRangeMax"]+1):
					subObjectiveJson["locationOfObjective"] = locationJson[str(i)]
					subObjectiveJson["locationOfObjective"]["rolledDice"] = diceResult

		return subObjectiveJson

	#TODO precisa trazer a tabela de vilao e fazer a logica de rolagem de vilao
	def defVillain(self):
		if self.contratJson["contractType"]["villainNeed"] == False:
			return

		f = open("json4Names/ContractServiceValueReward/villians.json")
		data = json.load(f)
		#TODO check this function, he are not working yet
		diceResult = self.dice.roll(1, 20)

		for i in data["contractType"]:
			if diceResult in range(data["contractType"][str(i)]["diceRangeMin"], data["contractType"][str(i)]["diceRangeMax"]+1):
				self.contratJson["contractType"] = data["contractType"][str(i)]
				self.contratJson["contractType"]["rolledDice"] = diceResult

		f.close()
		pass