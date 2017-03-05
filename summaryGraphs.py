import sys
import argparse
from botapi import Botagraph, BotApiError
from reliure.types import Text 

from collections import namedtuple
import codecs
import requests
import re
import csv

from botapad import *

#. Assumes that the vertice data are separated from the links ==> todo: generalize to any format
# and that the links are ordered with the same 2 types always at the same position within an edgetype
#(e.g. person -- infraction for all the links or infraction -- person for all the links of an edgetype)
#todo : make a systematic check
# todo: store the properties when needed

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

        if current[0]==0:
            rows = [re.split(' -- | >> | << ',x[0]) for x in rows]
            self.edges[current[1]] = [[x[0].strip(),x[1].strip()] for x in rows]
        else:
            self.vertices[current[1]] = dict([[x[0].strip(),x[1].strip()] for x in rows])
            for x in rows:
                self.vtype[x[0].strip()]=current[1]
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
                    pair =[self.vtype[edge[0]],self.vtype[edge[1]]]
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
        if self.vtype[self.edges[links][0][0]]==type1 and self.vtype[self.edges[links][0][1]]==type2:
            return [0,1]
        elif self.vtype[self.edges[links][0][1]]==type1 and self.vtype[self.edges[links][0][0]]==type2:
            return [1,0]
        else:
            print 'oups, vertices and edges do not correspond'
            sys.exit()
        

    def histo(self,type1,type2,links):
        
        # Create SummaryGraph object to store the histograph
        histograph = SummaryGraph()

    	# writes a framapad padagraph format file
    	fname = links+'_histograph.txt'
        s = open(fname,'w')

        # write the imports of  data file and set the separator
        s.write('!;\n\n& '+self.urls[type2]+'\n\n')
        histograph.urls[type2]= self.urls[type2]
       
        # Count the variable distribution
        order = self.checkOrder(type1,type2,links)
        counts = {}
        for x in self.edges[links]:    
            counts[x[order[1]]]= counts.get(x[order[1]],0) + 1
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
            p.sort()
            i = p[p.index(counts[x][1])-1]
            pnodes[(i,i+step)].append(x)
            p.remove(counts[x][1])

        # Write the list of the scale nodes
        s.write('\n\n@ Percent: #label, shape\n\n')
        histograph.vertices['Percent']={}
        # histograph.vprop
        sci = {}
        for x in pnodes:
            if len(pnodes[x])>0:
            	idnode = str(x[0])+'_to_'+str(x[1])
                s.write(idnode+'; circle\n')
                sci[x[0]]=idnode
                histograph.vertices['Percent'][idnode]=idnode

        # Makes links between 'percent' nodes to create a visual scale
        s.write('\n\n_ Scale\n\n')
        histograph.edges['Scale']=[]
        sci = sci.values()
        sci.sort(key = lambda w:w[0])
        for n in range(len(sci[:-1])):
            s.write(sci[n]+' -- '+sci[n+1]+'\n')
            histograph.edges['Scale'].append((sci[n],sci[n+1]))

        # Write the data links of the histograph
        s.write('\n\n_ Distribution: label\n\n')
        histograph.edges['Distribution']=[]
        for x in pnodes:
            for y in pnodes[x]:
                s.write(str(x[0])+'_to_'+str(x[1])+' -- '+y+'; '+str(counts[y][0])+' items and '+str(counts[y][1])+' pct\n')
                histograph.edges['Distribution'].append((str(x[0])+'_to_'+str(x[1]),y))
                #histograph.eprop['Distribution']

        s.close()
        print 'The file '+fname+' is ready to be imported in framadap!'
        return histograph


    def joinlinks(self,type1,type2,records,link1,link2):

        # Dictionay for crossing type1 and type2 with records
        counts = {}
        # Get the type1 to record links
        order = self.checkOrder(records,type1,link1)
        for x in self.edges[link1]: 
            if not counts.has_key(x[order[0]]):   
                counts[x[order[0]]] = {link1:[],link2:[]}
            counts[x[order[0]]][link1].append(x[order[1]])
        
        # Get the type2 to records links
        order = self.checkOrder(records,type2,link2)
        for x in self.edges[link2]: 
            if not counts.has_key(x[order[0]]):   
                counts[x[order[0]]] = {link1:[],link2:[]}
            counts[x[order[0]]][link2].append(x[order[1]])

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

    	# Open and write the begining of the pad, separator and imports 
    	fname = type1+'_distribution_by_'+type2+'.txt'
    	s = open(fname,'w')
        s.write('!;\n\n& '+self.urls[type1]+'\n& '+self.urls[type2]+'\n')
        dis.vertices[type1]=self.vertices[type1]
        dis.vertices[type2]=self.vertices[type2]

        # Write edgetype and label property
        s.write('\n_ Distribution: label\n\n')
        dis.edges['Distribution']=[]
        
        # Build the join between the two types
        linkdico = self.joinlinks(type1,type2,records,link1,link2)

        # Count the percentages
        for x in linkdico:
            total = float(sum(linkdico[x].values()))
            for y in linkdico[x]:
                linkdico[x][y]=[linkdico[x][y],round(linkdico[x][y]*100/total,2)]
            # Write the links
            for y in linkdico[x]:
                s.write(x+' >> '+y+'; '+str(linkdico[x][y][0])+' items, '+str(linkdico[x][y][1])+' pct\n')	
                dis.edges['Distribution'].append((x,y))
                #properties

        print 'The file '+fname+' is ready to be imported in framadap!'
        s.close()
        return dis


    def metagraph(self,fname):

    	# Describes the relations between the variables of a dataset
        # write the file and create a SummaryGraph object
        # todo : split the 2 in 2 functions
        meta = SummaryGraph()
        s = open(fname,'w')
        s.write('!;\n\n')
        for x in self.vertices: 
            s.write('\n@ '+x.encode('utf-8')+': #label\n')
            s.write(x.encode('utf-8')+'\n')
            meta.vertices[x]={x:x}
        for x in self.evtype:
            s.write('\n_ '+x.encode('utf-8')+': label\n')
            meta.edges[x] = []
            for y in self.evtype[x]:
                s.write(y[0].encode('utf-8')+' -- '+y[1].encode('utf-8')+'; '+str(self.evtype[x][y])+'\n')
                meta.edges[x].append([y[0],y[1]])
        print 'The file'+fname+' is ready to be imported in framadap!'
        s.close()
        return meta


    # todo : write any summaryGraph object into a Pad
    def writePad(self,data_file,edges_file):

        sdata = open(data_file,'w')
        sedges = open(edges_file,'w')
        sdata.write('!;\n\n')
        sedges.write('!;\n\n')
        #
        #
        for x in self.edges:
            sedges.write('_ '+x)
        #    self.vprop
        for x in self.vertices:
            sdata.write('@ '+x)
        #    self.eprop
        sdata.close()
        sedges.close()


if __name__ == '__main__':
    print '\n\b\n** Testing with the Corruption dataset **\n\n'
    h = SummaryGraph()
    h.parse('https://mensuel.framapad.org/p/corruptionGraph')
    h.show()
    print 'Test the generation of the pads for the 3 types of graphs'
    histograph = h.histo('Personne','Infraction','PersonInfraction')
    d = h.distrib('EntiteImpliquee','Infraction','Personne','PersonEntite','PersonInfraction')
    meta = h.metagraph('metagraph.txt')
    #todo
    # meta.writePad()
    #histograph.writePad()
    