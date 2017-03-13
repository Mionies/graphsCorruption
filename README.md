# graphsCorruption

Mise en graphes des données d'affaires judiciaires liées à la corruption à travers 3 types de graphes: metagraphs, histographs subgraphs

### Post Blog mtdp draft link

https://docs.google.com/document/d/1DwO0pntgyaeBSQ3eomWMLDAVMhz3tUxeywGi2EUNCuk/edit?usp=sharing


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


### Data Graph Links

http://www.padagraph.io/graph/InfractionRegionAffaire


### Pad contenant la totalite des vertices et des liens utilises ailleurs

https://mensuel.framapad.org/p/corruptionGraph

## summaryGraph.py

génère des histographes, graphes de distribution et un metagaphe basic à partir de données au format padagraph sur framapad

todo: généraliser pour accepter tout ce qui est accepté par le parser botapad 

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
