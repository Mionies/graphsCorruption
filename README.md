# graphsCorruption

Mise en graphes des données d'affaires judiciaires liées à la corruption à travers 3 types de graphes

### Post Blog mtdp draft link

https://docs.google.com/document/d/1DwO0pntgyaeBSQ3eomWMLDAVMhz3tUxeywGi2EUNCuk/edit?usp=sharing


### Metagraph Link

http://public.padagraph.io/graph/MetaGraphCorruption

https://mensuel.framapad.org/p/metagraph

### Histograph Links
#### Entité

http://padagraph.io/graph/CasePercentageEntity

https://mensuel.framapad.org/p/corruptionGraphPercentEntity

#### Région

http://padagraph.io/graph/CasePercentageRegion

https://mensuel.framapad.org/p/corruptionGraphPercentRegion

#### Secteur

https://mensuel.framapad.org/p/corruptionGraphPercentTag

#### Infraction



### Distribution graphs Links


### Data Graph Links

http://padagraph.io/graph/PersonInfraction

### Données pour normaliser les histographes

https://fr.wikipedia.org/wiki/Liste_des_d%C3%A9partements_fran%C3%A7ais_class%C3%A9s_par_population_et_superficie

https://fr.wikipedia.org/wiki/R%C3%A9gion_fran%C3%A7aise


### Pad contenant la totalite des vertices et des liens utilises ailleurs

https://mensuel.framapad.org/p/corruptionGraph

## summaryGraph.py

génère des histographes, graphes de distribution et un metagaphe basic à partir de données au format padagraph sur framapad

todo: généraliser pour accepter tout ce qui est accepté par le parser botapad 

#### Usage

g = SummaryGraph()

g.parse(url)

metagraph = g.meta(file_name)

h = g.histo(v1,v2,e)

d = g.distrib(v1,v2,record,e1,e2)
