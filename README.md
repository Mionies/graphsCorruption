# graphsCorruption

Mise en graphes des données d'affaires judiciaires liées à la corruption à travers 4 types de graphes: metagraphes, histographes, distribution d'une variable par rapport à une autre et sousgraphes


### Metagraph Link

http://public.padagraph.io/graph/MetaGraphCorruption

https://mensuel.framapad.org/p/metagraph

### Histograph Links
Secteur:http://www.padagraph.io/graph/HistographSecteurCorruption

Infraction: http://www.padagraph.io/graph/HistographInfractionCorruption

Graph Entite: http://www.padagraph.io/graph/HistographEntiteCorruption

Region: http://www.padagraph.io/graph/HistographRegionCorruption

Entite http://www.padagraph.io/graph/HistographEntiteCorruption


### Distribution graphs Links

Infraction par Secteur: http://www.padagraph.io/graph/DistributionInfractionparSecteur

Secteur par Infraction: http://www.padagraph.io/graph/DistributionSecteurparInfraction

Infraction par Région: http://www.padagraph.io/graph/DistributionInfractionparRegion

Entité par Infraction: http://www.padagraph.io/graph/DistributionEntiteparInfraction

Infraction par Entité: http://www.padagraph.io/graph/DistributionInfractionparEntité


### Sous-graphes

http://www.padagraph.io/graph/InfractionRegionAffaire


### Pad contenant la totalite des vertices et des liens utilises ailleurs

http://www.padagraph.io/graph/GraphCorruptionToutesInfos

https://mensuel.framapad.org/p/corruptionGraph

## summaryGraph.py

Génère des histographes, graphes de distribution des sous-graphes et un metagaphe basic à partir de données au format padagraph sur framapad

TODO: généraliser pour accepter tout ce qui est accepté par le parser botapad 

#### Usage

* h = SummaryGraph()
* h.parse('https://mensuel.framapad.org/p/corruptionGraph')
* h.show()

* histograph = h.phisto('Personne','Région'.decode('utf-8'),'PersonRegion')
* d = h.distrib('EntiteImpliquee','Infraction','Personne','PersonEntite','PersonInfraction')
* subg = h.subgraph(['Personne','Région'.decode('utf-8'),'Infraction'])
* meta = h.metagraph()
* nh = h.norm_histo('Personne','Région'.decode('utf-8'),'Population','PersonRegion')

* meta.writePad('output_file_prefix')
* histograph.writePad('output_file_prefix')
