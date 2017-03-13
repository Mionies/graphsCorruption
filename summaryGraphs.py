# -*- coding: utf-8 -*-

import sys
import argparse

from collections import namedtuple
import codecs
import requests
import re
import csv

from botapad import *

# assumes As that the links are ordered with the same 2 types always at the same position within an edgetype
#(e.g. person -- infraction for all the links or infraction -- person for all the links of an edgetype)
#todo : make a systematic check
 


class SummaryGraph(object):

    def __init__(self):
        """ Function doc
        :param : 
        """
        self.vertices = {}
        self.edges = {}
        self.urls = {}
        self.vtype = {}
        self.evtype = {}
        self.vprop = {}
        self.eprop = {}
        #todo
        #self.edir = {}



    def read(self, path, separator='auto'):

        if path[0:4] == 'http':
            try : 
                url = convert_url(path)
                log( " * Downloading %s \n" % url)
                content = requests.get(url).text
                lines = content.split('\n')
            except :
                raise BotapadURLError("Can't download %s" % url, url)
        else:
            log( " * Opening %s \n" % path)
            try : 
                with codecs.open(path, 'r', encoding='utf8' ) as fin:
                    lines = [ line for line in fin]
            except :
                raise BotapadError("Can't read file %s" % path)

        lines = [ line.strip() for line in lines ]
        lines = [ line.encode('utf8') for line in lines if len(line)]
        
        if separator == u'auto':
            line = lines[0].strip()
            if line in ( '!;','!,'):
                separator = line[1:]
            else: separator = ','

        log(" * Reading %s (%s) lines with delimiter '%s'" % (path, len(lines), separator))

        try : 
            reader = csv.reader(lines, delimiter=separator)
            rows = [ r for r in reader]
            rows = [ [ e.strip().decode('utf8')  for e in r ] for r in rows if len(r) and not all([ len(e) == 0 for e in r]) ]
        except :
            raise BotapadCsvError(path, separator, "Error while parsing data %s lines with separator %s" % (len(lines), separator )  )

        return rows

                    
    def store(self,current,rows,path):
        # store graph labels and properties for edges and vertices


        if current[0]==0:
            for n in range(len(rows)):
                l = [re.split(' -- | >> | << ',rows[n][0])]
                l = [[x[0].strip(),x[1].strip()] for x in l]
                l.extend(rows[n][1:])
                rows[n]= l
            self.edges[current[1]] = rows[:]
            if len(current[2])>0:
                self.eprop[current[1]] = [x.name for x in current[2]]
        else:
            self.vertices[current[1]] = dict([[x[0].strip(),x[1:]] for x in rows])
            for x in rows:
                self.vtype[x[0].strip()]=current[1]
            if len(current[2])>0:
                self.vprop[current[1]] = [x.name for x in current[2]]
        self.urls[current[1]]=path



    def parse(self, path):
        """ :param path : txt file path

        handles special lines starting with [# @ _]
        for comments, node type, property names
        
        """
        csv = self.read(path)
        
        rows = []
        current = () # (VERTEX | EDGE, label, names, index_prop)
        
        
        for row in csv:
            cell = row[0]
            # ! comment
            if cell[:1] == "!":
                continue

            # IMPORT external ressource
            if cell[:1] == "&":
                url = cell[1:].strip()
                self.parse(url)
                    
            # @ Nodetypes, _ Edgetypes
            elif cell[:1] in ("@", "_"):
                if len(current)>0:
                    self.store(current,rows,path)
                # processing directiv
                line = ";".join(row)
                cols = re.sub(' ', '', line[1:]) # no space
                # @Politic: %Chamber; #First Name; #Last Name;%Party;%State;%Stance;Statement;
                cols = [e for e in re.split("[:;,]" , "%s" % cols, flags=re.UNICODE) if len(e)]
                label = cols[0] # @Something
                
                # ( name, type indexed, projection )
                props = [ Prop( norm_key(e), Text(multi="+" in e), "@" in e, "#" in e, "+" in e,  "%" in e, "+" in e and "=" in e ) for e in  cols[1:]]
                    
                if cell[:1] == "@": # nodetype def
                    rows = []
                    current = (VERTEX, label, props)
                        
                elif cell[:1] == "_": # edgetype def
                    rows = []
                    current = (EDGE, label, props)
            else: # table data
                if current and current[2]:
                    for i, v in enumerate(row):
                        if i >= len(props): break
                        if props[i].ismulti :
                            row[i] = [  e.strip() for e in re.split("[_,;]", v.strip(), ) ] 
                            
                rows.append(row)

        self.store(current,rows,path)



    def EdgesToVertices(self):

        # Edges between which 2 types of vertices
        for x in self.edges:
                self.evtype[x]={}
                for edge in self.edges[x]:
                    pair =[self.vtype[edge[0][0]],self.vtype[edge[0][1]]]
                    pair.sort()
                    self.evtype[x][tuple(pair)] =self.evtype[x].get(tuple(pair), 0) + 1



    def show(self):

        # display nodes and edges + edgetypes
        print 'Vertices:'
        for x in self.vertices.keys():
            print x,'\t', self.urls[x]
        print '\nEdges:'
        self.EdgesToVertices()
        for x in self.edges.keys():
            print x,'\t', self.urls[x],'\t',self.evtype[x]



    def checkOrder(self,type1,type2,links):

        # in an edge, which on is type1 and whoch one is type2
        if self.vtype[self.edges[links][0][0][0]]==type1 and self.vtype[self.edges[links][0][0][1]]==type2:
            return [0,1]
        elif self.vtype[self.edges[links][0][0][1]]==type1 and self.vtype[self.edges[links][0][0][0]]==type2:
            return [1,0]
        else:
            print 'oups, vertices and edges do not correspond'
            sys.exit()



    def ChangeShape(self, vtype, shape):

        # Change the shape of a vertice, modify it if specified, add it if not
        # default shape is circle
        v = self.vertices[vtype].items()   
        if 'shape' in self.vprop[vtype]:
            i = self.vprop[vtype].index('shape')-1
            for n in range(len(v)):
                v[n] = list(v[n])
                v[n][1][i]=shape
        else:
            v = [x[1].append(shape) for x in v]
            self.vprop[vtype].append('shape')



    def Star(self,vtype):
        
        # Star all the nodes of a nodetype
        d = {}
        for idv in self.vertices[vtype]:
            d['*'+idv]= self.vertices[vtype][idv]

        self.vertices[vtype]=d



    def phisto(self,type1,type2,links):
        
        # Create SummaryGraph object to store the histograph

        histograph = SummaryGraph()

        # store type2 vertices and edges
        # change shape to triangle
        # star the type2 nodes

        histograph.urls[type2]= self.urls[type2]
        histograph.vprop[type2] = self.vprop[type2]
        histograph.vertices[type2] = self.vertices[type2]
        histograph.Star(type2)
        histograph.ChangeShape(type2,'triangle')    
       
        # Count the variable distribution

        order = self.checkOrder(type1,type2,links)
        counts = {}
        for x in self.edges[links]:    
            counts[x[0][order[1]]]= counts.get(x[0][order[1]],0) + 1
            #counts[x[0][order[1]]]= counts[x[0][order[1]]]/self.
        for x in counts:
            counts[x]=[counts[x],round(counts[x]*100/float(len(self.edges[links])),2)]
     
        # Set the scale

        percents = [x[1] for x in counts.values()]
        rangep =  max(percents) - min(percents)
        step = round(rangep/10.0,0)
        pnode = int(min(percents))
        pnodes = {}
        p = []

        # Create a scale 

        while pnode<max(percents):
            pnodes[(pnode,pnode+step)]=[]
            p.append(pnode)
            pnode+=step

        # Put eache node on the scale

        for x in counts:
            p.append(counts[x][1])
            p.sort(key = lambda w:float(w))
            i = p[p.index(counts[x][1])-1]
            pnodes[(i,i+step)].append(x)
            p.remove(counts[x][1])

        # list of the scale nodes

        histograph.vertices['Percent']={}

        sci = []
        for x in pnodes:
            if len(pnodes[x])>0:
            	idnode = str(x[0])+'_to_'+str(x[1])
                sci.append((x[0],idnode))
                histograph.vertices['Percent']['*'+idnode]=[str(len(pnodes[x])),'http://icons.iconarchive.com/icons/iconarchive/red-orb-alphabet/256/Percent-icon.png', 'circle']
                histograph.vprop['Percent']=['label','Nombre de cas','image','shape']

        # Makes links between 'percent' nodes to create a visual scale

        histograph.edges['Scale']=[]
        sci.sort(key = lambda w:w[0])
        for n in range(len(sci[:-1])):
            histograph.edges['Scale'].append([[sci[n][1],sci[n+1][1]]])

        # data links of the histograph
        histograph.edges['Distribution']=[]
        for x in pnodes:
            for y in pnodes[x]:
                histograph.edges['Distribution'].append([[str(x[0])+'_to_'+str(x[1]),y],str(counts[y][1])+' pct ('+str(counts[y][0])+')'])
                histograph.eprop['Distribution'] = ['label']

        return histograph



    def norm_histo(self,type1,type2,prop,links):
        
        # Create SummaryGraph object to store the histograph

        nhist = SummaryGraph()

        # store type2 vertices and edges
        # change shape to triangle
        # star the type2 nodes

        nhist.urls[type2]= self.urls[type2]
        nhist.vprop[type2] = self.vprop[type2]
        nhist.vertices[type2] = self.vertices[type2]
        nhist.Star(type2)
        nhist.ChangeShape(type2,'triangle')    
       
       #norm prop
        idn = self.vprop[type2].index(prop)-1
        # Count the variable distribution

        order = self.checkOrder(type1,type2,links)
        counts = {}
        for x in self.edges[links]:    
            counts[x[0][order[1]]]= counts.get(x[0][order[1]],0)+1
            
        for x in counts:
            counts[x]=[counts[x],round(counts[x]*1000000/float(self.vertices[type2][x][idn]),2)]
     
        # Set the scale

        percents = [x[1] for x in counts.values()]
        rangep =  max(percents) - min(percents)
        step = round(rangep/10.0,0)
        pnode = int(min(percents))
        pnodes = {}
        p = []

        # Create a scale 

        while pnode<max(percents):
            pnodes[(pnode,pnode+step)]=[]
            p.append(pnode)
            pnode+=step

        # Put eache node on the scale

        for x in counts:
            p.append(counts[x][1])
            p.sort(key = lambda w:float(w))
            i = p[p.index(counts[x][1])-1]
            pnodes[(i,i+step)].append(x)
            p.remove(counts[x][1])

        # list of the scale nodes

        nhist.vertices['Percent']={}

        sci = []
        for x in pnodes:
            if len(pnodes[x])>0:
                idnode = str(x[0])+'_to_'+str(x[1])
                sci.append((x[0],idnode))
                nhist.vertices['Percent']['*'+idnode]=[str(len(pnodes[x])),'https://upload.wikimedia.org/wikipedia/commons/f/fd/Color_icon_red.svg', 'circle']
                nhist.vprop['Percent']=['label','Nombre de cas','image','shape']

        # Makes links between 'percent' nodes to create a visual scale

        nhist.edges['Scale']=[]
        sci.sort(key = lambda w:w[0])
        for n in range(len(sci[:-1])):
            nhist.edges['Scale'].append([[sci[n][1],sci[n+1][1]]])

        # data links of the histograph
        nhist.edges['Distribution']=[]
        for x in pnodes:
            for y in pnodes[x]:
                nhist.edges['Distribution'].append([[str(x[0])+'_to_'+str(x[1]),y],str(counts[y][1])+' pct ('+str(counts[y][0])+')'])
                nhist.eprop['Distribution'] = ['label']

        return nhist



    def joinlinks(self,type1,type2,records,link1,link2):

        # Dictionay for crossing type1 and type2 with records
        counts = {}
        # Get the type1 to record links
        order = self.checkOrder(records,type1,link1)
        for x in self.edges[link1]: 
            if not counts.has_key(x[0][order[0]]):   
                counts[x[0][order[0]]] = {link1:[],link2:[]}
            counts[x[0][order[0]]][link1].append(x[0][order[1]])
        
        # Get the type2 to records links
        order = self.checkOrder(records,type2,link2)
        for x in self.edges[link2]: 
            if not counts.has_key(x[0][order[0]]):   
                counts[x[0][order[0]]] = {link1:[],link2:[]}
            counts[x[0][order[0]]][link2].append(x[0][order[1]])

        # Build the type2 and type1 links
        linkdico = {}
        for x in counts:
            for a in counts[x][link1]:
                if not linkdico.has_key(a):
                    linkdico[a] ={}
                for b in counts[x][link2]:
                    if not b in linkdico[a]:
                        linkdico[a][b] = 0
                    linkdico[a][b]+=1
        return linkdico   



    def distrib(self,type1,type2,records,link1,link2):
        
        #Create a SummaryGraph object
        dis = SummaryGraph()

    	# get vertices anf their properties + files urls
        dis.vertices[type1]=self.vertices[type1]
        dis.vertices[type2]=self.vertices[type2]
        dis.vprop[type1]=self.vprop[type1]
        dis.vprop[type2]=self.vprop[type2]
        dis.urls[type1] = self.urls[type1]
        dis.urls[type2] = self.urls[type2]
        dis.ChangeShape(type1,'circle')
        dis.ChangeShape(type2,'triangle')

        # edgetype and label property
       
        dis.edges['Distribution']=[]
        
        # Build the join between the two types
        linkdico = self.joinlinks(type1,type2,records,link1,link2)

        # Count the percentages
        for x in linkdico:
            total = float(sum(linkdico[x].values()))
            for y in linkdico[x]:
                linkdico[x][y]=[linkdico[x][y],round(linkdico[x][y]*100/total,2)]
  
            # the links
            for y in linkdico[x]:
                dis.edges['Distribution'].append([[x,y],str(linkdico[x][y][0])+' , '+str(linkdico[x][y][1])+' pct'])
                dis.eprop['Distribution']=['label']

        return dis



    def metagraph(self):

        special_props = ['image','label','shape']

    	# Describes the relations between the variables of a dataset
        meta = SummaryGraph()

        meta.vertices['Properties'] = {}
        meta.edges['Properties'] =[]
        meta.vprop['Properties']=['#label','shape']
        meta.eprop['Properties']=[]

        for x in self.vertices: 
            meta.vertices[x]={x:['triangle']}
            meta.vprop[x]=['#label','shape']

            # create vertices for properties
            for p in self.vprop[x]:
                if not p in special_props:
                    meta.vertices['Properties'][p]=['triangle']
                    meta.edges['Properties'].append([[p,x]])

        # Create nodes edges
        for x in self.evtype:
            meta.edges[x] = []
            for y in self.evtype[x]:
                meta.edges[x].append([[y[0],y[1]],str(self.evtype[x][y])])
                meta.eprop[x]=['label']

        return meta


    def subgraph(self,vlist):

        if len(self.evtype)==0:
            self.EdgesToVertices()

        elist = []

        for x in self.evtype:
            for y in self.evtype[x]:
                if y[0] in vlist and y[1] in vlist:
                    elist.append(x)

        sub = SummaryGraph()

        for x in vlist:
            sub.vertices[x] = self.vertices[x]
            sub.vprop[x] = self.vprop[x]

        for x in elist:
            sub.edges[x] = self.edges[x]
            try:
                sub.eprop[x] = self.eprop[x]
            except:
                pass

        return sub

    def writePad(self, prefix):

        sdata = open(prefix+'_data.txt','w')
        sedges = open(prefix+'_edges.txt','w')
        sdata.write('!;\n\n')
        sedges.write('!;\n\n')
        #
        # Write the edges file
        for x in self.edges:
            sedges.write('\n_ '+x.encode('utf-8'))
            if self.eprop.has_key(x):
                sedges.write(': '+', '.join(self.eprop[x])+'\n\n')
            else:
                sedges.write('\n')
            for e in self.edges[x]:
                sedges.write(e[0][0].encode('utf-8')+' -- '+e[0][1].encode('utf-8'))
                if len(e)>1:
                    sedges.write('; '+'; '.join(e[1:])+'\n')
                else:
                    sedges.write('\n')
            sedges.write('\n')

        # Write de data file                
        for x in self.vertices:
            sdata.write('\n@ '+x.encode('utf-8'))
            sdata.write(': '+', '.join([w.encode('utf-8') for w in self.vprop[x]])+'\n\n')
            for v in self.vertices[x]:
                sdata.write(v.encode('utf-8'))
                if len(self.vertices[x][v])>0:
                    sdata.write('; '+'; '.join([ w.encode('utf-8') for w in self.vertices[x][v]])+'\n')
                else: 
                    sdata.write('\n')
            sdata.write('\n')

        sdata.close()
        sedges.close()



if __name__ == '__main__':
    print '\n\b\n** Testing with the Corruption dataset **\n\n'
    h = SummaryGraph()
    h.parse('https://mensuel.framapad.org/p/corruptionGraph')
    h.show()

    print '\nTest writting pads for the 5 types of graphs\n'
    histograph = h.phisto('Personne','Région'.decode('utf-8'),'PersonRegion')
    d = h.distrib('EntiteImpliquee','Infraction','Personne','PersonEntite','PersonInfraction')
    subg = h.subgraph(['Personne','Région'.decode('utf-8'),'Infraction'])
    meta = h.metagraph()
    nh = h.norm_histo('Personne','Région'.decode('utf-8'),'Population','PersonRegion')

    # Generer tous les histo pertinents
    print "creating histo 1"
    hist1 = h.phisto('Personne','Région'.decode('utf-8'),'PersonRegion')
    hist1.writePad('h_region')
    print "creating histo 2"
    hist2 = h.phisto('Personne','EntiteImpliquee','PersonEntite')
    hist2.writePad('h_entite')
    print "creating histo 3"
    hist3 = h.phisto('Personne','Infraction','PersonInfraction')
    hist3.writePad('h_infraction')
    print "creating histo 4"
    hist4 = h.phisto('Personne','Annee','PersonYear')
    hist4.writePad('h_annee')
    print "creating histo 5"
    hist5 = h.phisto('Personne','Tags','PersonTag')
    hist5.writePad('h_secteur')

    
    # Generer toutes les distrib pertinentes
    print "creating distr 11"
    d11 = h.distrib('EntiteImpliquee','Infraction','Personne','PersonEntite','PersonInfraction')
    d11.writePad('infrac_par_entite')
    print "creating distr 12"
    d12= h.distrib('Infraction','EntiteImpliquee','Personne','PersonInfraction','PersonEntite')
    d12.writePad('entite_par_infrac')
    print "creating distr 21"
    d21 = h.distrib('Région'.decode('utf-8'),'Infraction','Personne','PersonRegion','PersonInfraction')
    d21.writePad('infrac_par_region')
    print "creating distr 22"
    d22 = h.distrib('Infraction', 'Région'.decode('utf-8'),'Personne','PersonInfraction','PersonRegion',)
    d22.writePad('region_par_infrac')


    print 'Test writting graphs in pads'
    meta.writePad('meta')
    histograph.writePad('histo')
    d.writePad('distr')
    h.writePad('htest')
    nh.writePad('nh')
    subg.writePad('subgraph')
    