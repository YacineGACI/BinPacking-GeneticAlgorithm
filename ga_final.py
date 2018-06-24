import random, operator, copy, numpy

class GeneticAlgoritm:
    def __init__(self, itemList,populationSize=100, crossoverP=0.5, mutationP=0.5, binCapacity=15, fitnessParam=0.4, selectedParents=20, nbIterations=100,nbmutationP=0.5, selectionType="standard", alwaysMutate=False,cutLength=2, newGenerationSelection="children",selectionBestP=1):
        self.populationSize = populationSize
        self.crossoverP = crossoverP
        self.mutationP = mutationP
        self.population = []
        self.binCapacity = binCapacity
        self.itemList = itemList
        self.fitnessParam = fitnessParam
        self.selectedParents = selectedParents
        self.nbIterations = nbIterations
        self.nbmutationP = nbmutationP # percent taille mutation
        self.alwaysMutate = alwaysMutate
        self.cutLength=cutLength
        self.selectionBestP=selectionBestP
        if selectionType == "standard":
            self.selection = self.roulette
        else:
            self.selection = self.selectParents

        if newGenerationSelection == "bestFitness":
            self.run = self.runBestFitness
        else:
            self.run = self.runOnlyChildren

    def generateInitialiPopulation(self):
        for i in range(self.populationSize):
            self.population.append(self.firstFit())


    def firstFit(self):
        bins = [[]]
        itemListShuffled = self.itemList.copy()
        random.shuffle(itemListShuffled)
        for i in range(len(itemListShuffled)):
            put = False
            for j in range(len(bins)):
                if itemListShuffled[i] <= self.binCapacity - sum(bins[j]):
                    bins[j].append(itemListShuffled[i])
                    put = True
                    break
            if put is False:
                bins.append([itemListShuffled[i]])
        return bins

    def fitness(self, individual):
        fitness = 0
        for i in range(len(individual)):
            fitness += (sum(individual[i])/self.binCapacity) ** self.fitnessParam
        return fitness/len(individual)

    def selectParents(self):
        fitnessList = {}
        for i in range(len(self.population)):
            fitnessList[i] = self.fitness(self.population[i])
        tmp = sorted(fitnessList.items(), key=operator.itemgetter(1), reverse=True)[:self.selectedParents]
        parents = []
        for i in tmp:
            parents.append(self.population[i[0]])
        return parents


    def rouletteVersionA(self):
        fitnessList = {}
        for i in range(len(self.population)):
            fitnessList[i] = self.fitness(self.population[i])
        fitnessList = [f/sum(fitnessList) for f in fitnessList]
        i = 0
        parents = []
        population = copy.deepcopy(self.population)
        while i < self.selectedParents:
            p = random.choices(population, weights=fitnessList)
            if p not in parents:
                parents.append(p)
                i += 1
        return parents


    def roulette(self):
        fitnessList = {}
        for i in range(len(self.population)):
            fitnessList[i] = self.fitness(self.population[i])
        fitnessList = [f/sum(fitnessList) for f in fitnessList]
        population = copy.deepcopy(self.population)
        return list(numpy.random.choice(population, size=self.selectedParents, replace=False, p=fitnessList))







    
    def generateBabies(self, parent, toInsertBins):
        tmp = copy.deepcopy(toInsertBins)
        i = 0
        nbIter = len(parent)
        while i < nbIter: #loop throught the bins of the parent
            binWillBeRemoved = False
            for j in range(len(parent[i])): #loop throught the items of the parent bin
                for k in range(len(tmp)): #loop throught the bins to insert
                    if parent[i][j] in tmp[k]:
                        tmp[k].remove(parent[i][j])
                        binWillBeRemoved = True
                        break
            if binWillBeRemoved:
                parent.pop(i)
                nbIter -= 1
            else:
                i += 1
        #add toInsertBins to the parent
        parent += toInsertBins
        notInserted= copy.deepcopy(self.itemList)
        for singleBin in parent:
            for item in singleBin:
                if item in notInserted:
                    notInserted.remove(item)
        return parent, notInserted


    def replacement(self, baby, notInserted):
        for step in[3,2]:
            for i in range(len(baby)):
                baby[i] = sorted(baby[i])
            i = 0
            nbIter = len(notInserted)
            while i < nbIter:
                replaced=False
                for ii in range(len(baby)):
                    j = 0
                    precedent = 0
                    while j+step <= len(baby[ii]):
                        if sum(baby[ii][j:j+step]) <= notInserted[i] and sum(baby[ii])-sum(baby[ii][j:j+step]) + notInserted[i] <= self.binCapacity:
                            precedent = j
                            j += 1
                        else :
                            break
                    if j > 0:
                        for k in range(step):
                            notInserted.append(baby[ii][precedent])
                            baby[ii].remove(baby[ii][precedent])
                        baby[ii].append(notInserted[i])
                        notInserted.remove(notInserted[i])
                        nbIter += step - 1
                        baby[ii] = sorted(baby[ii])
                        replaced=True
                        break
                if not replaced:
                    i += 1
        return baby, notInserted

    
    def grow(self, baby, notInserted):
        notInserted = sorted(notInserted)

        #itemListShuffled = self.itemList.copy()
        #random.shuffle(itemListShuffled)
        #tmpList = []
        nbIteration=len(baby)
        for i in range(len(notInserted)):
            put = False
            j=0
            while j <nbIteration:
                if notInserted[i] <= self.binCapacity - sum(baby[j]):
                    baby[j].append(notInserted[i])
                    put = True
                    break
                j+=1    
            if put is False:
                baby.append([notInserted[i]])
                nbIteration+=1
        return baby


    
    def crossOver(self, p1, p2):
        #crossoverP
        cross=  random.randint(0, 100)/100
        if cross<self.crossoverP:
            cut1 = random.randint(0, len(p1) - self.cutLength)
            cut2 = random.randint(0, len(p2) - self.cutLength)
            tmp1 = []
            tmp2 = []
            for i in range(self.cutLength):
                tmp1.append(p1.pop(cut1))
                tmp2.append(p2.pop(cut2))
            c1, notInserted1 = self.generateBabies(p1, tmp2)
            c2, notInserted2 = self.generateBabies(p2, tmp1)

            c1, notInserted1 = self.replacement(c1, notInserted1)
            c2, notInserted2 = self.replacement(c2, notInserted2)
            #print('c1',c1,'notinser1',notInserted1)
            c1 = self.grow(c1, notInserted1)
            c2 = self.grow(c2, notInserted2)
            #print('c1',c1)
            return c1, c2
        else:
            return p1, p2


    def mutation(self,child):
        mut=  random.random()
        if mut < self.mutationP and len(child)>1 :
            twin = copy.deepcopy(child)
            nbmutation=random.randint(1, int(len(child)*self.nbmutationP))
            notInserted= []

            for i in range(nbmutation) :         
                binDeleted = random.randint(0, len(child)-1)
                notInserted+=child[binDeleted]
                child.pop(binDeleted) 
            child, notInserted = self.replacement(child, notInserted)
            child=self.grow(child, notInserted)   
            if self.alwaysMutate is False and self.fitness(child) > self.fitness(twin):
                return child
            else:
                return twin
        return child
    


    def generateChildren(self, parents):
        children = []
        random.shuffle(parents)
        while len(parents) != 0:
            c1, c2 = self.crossOver(parents.pop(0), parents.pop(0))
            c1 = self.mutation(c1)
            c2 = self.mutation(c2)
            children.append(c1)
            children.append(c2)
        return children


    def solution(self,children):
        return sorted(children, key=lambda v: len(v))[0]


    def populationCream(self, population):
        fitnessList = {}
        for i in range(len(population)):
            fitnessList[i] = self.fitness(population[i])
        tmp = sorted(fitnessList.items(), key=operator.itemgetter(1), reverse=True)[:int(self.populationSize*self.selectionBestP)]
        tmp += sorted(fitnessList.items(), key=operator.itemgetter(1))[:self.populationSize-int(self.populationSize*self.selectionBestP)]

        parents = []
        for i in tmp:
            parents.append(population[i[0]])
        return parents

    

    def runBestFitness(self):
        self.generateInitialiPopulation()
        best = self.solution(self.population)
        for i in range(self.nbIterations):
            parents = self.selection()
            children = copy.deepcopy(self.generateChildren(parents))
            self.population = copy.deepcopy(self.populationCream(children+self.population))
            if len(self.solution(self.population)) < len(best):
                best = copy.deepcopy(self.solution(self.population))
            sizes = [len(t) for t in self.population]
            print(sizes)
        print(best)    


    def runOnlyChildren(self):
        self.generateInitialiPopulation()
        best = self.solution(self.population)
        for i in range(self.nbIterations):
            self.population  = copy.deepcopy(self.generateChildren(self.population))
            if len(self.solution(self.population)) < len(best):
                best = copy.deepcopy(self.solution(self.population))
            sizes = [len(t) for t in self.population]
            print(sizes)
        print(best)    
 
  



if __name__=="__main__":
    ga = GeneticAlgoritm(itemList=[1,2,3,4,5,6,7,8,9,10,11,12,13,14], populationSize=6, crossoverP=0.9, mutationP=0.1, binCapacity=15, fitnessParam=2, selectedParents=4, nbIterations=100,nbmutationP=0.7, selectionType="roulette", alwaysMutate=False,cutLength=2,newGenerationSelection="bestFitness",selectionBestP=1)
    # ga = GeneticAlgoritm(6, 0.9, 0.1, 15, [1,5,8,6,5,9,3,6,5,4,9,7,12,15,6,12], 2, 2, 1)
    ga.run()