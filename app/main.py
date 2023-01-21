import logging
import os
import sys
import time
from typing import Any, Dict

import graphistry
from dotenv import load_dotenv
from fastapi import FastAPI
from neo4j import GraphDatabase  # for data loader

load_dotenv()
uri=os.getenv("uri")
user=os.getenv("user")
pwd=os.getenv("pwd")


# graphistry.register(api=3, username='jagadeesh_aarth', password='Prat2020')
# graphistry.register(api=3, token=initial_one_hour_token)
# graphistry.register(api=3,personal_key_id='N11OMK682O', personal_key_secret='3D9JMTGATJNRQXE0', protocol='https', server='hub.graphistry.com')
NEO4J={'uri':"bolt://localhost:7687", 'auth':("neo4j", "Admin@123")}
graphistry.register(bolt=NEO4J)


def connection():
  driver=GraphDatabase.driver(uri=uri,auth=(user,pwd))
  return (driver)

app = FastAPI()   
@app.get("/") 
async def main_route():     
    load_dotenv()
    uri=str(os.getenv("uri"))
    user=str(os.getenv("user"))
    pwd=str(os.getenv("pwd"))
    driver=GraphDatabase.driver(uri=uri,auth=(user,pwd))
    session=driver.session()
    q1="""
    Match(n) return count(n) as count
    """
    results=session.run(q1)
    li=[r["count"] for r in results]
    result={"count":li}
    return result



@app.post("/journal/")
async def create_journal(request:Dict = None):
    logger = setup_custom_logger('create_journal')
    load_dotenv()
    uri=str(os.getenv("uri"))
    user=str(os.getenv("user"))
    pwd=str(os.getenv("pwd"))
    driver=GraphDatabase.driver(uri=uri,auth=(user,pwd))
    session=driver.session()
    data=request #.decode('utf-8')
    # data= json.load(codecs.decode(request.data,'utf-8-sig'))
    # print (data)
    keys=list(data.keys())
    simple_keys=[]
    for key in keys:
        if isinstance(data[key],dict) or isinstance(data[key],str):
            simple_keys.append(key)

    for simple_key in simple_keys:     
            if simple_key == "JournalReference":
                rJournalReference=data[simple_key]
                referenceDOI=rJournalReference.get("doi")
                referenceTitle=rJournalReference.get("title")
                referenceDOIURL=rJournalReference.get("doiURL")
                authorScopusID=rJournalReference.get("authorScopusID")
            elif simple_key=="Affiliation":
                rAffiliation=data[simple_key]
            elif simple_key=="Year":
                rYear=data[simple_key]
            elif simple_key=="Conceptual":
                rConceptual=data[simple_key]
            elif simple_key=="JournalPublication":
                rJournalPublication=data[simple_key]
            elif simple_key=="Publisher":
                rPublisher=data[simple_key]
                vPublisherName=rPublisher['name']
            elif simple_key=="Empirical":
                rEmpirical=data[simple_key]
            elif simple_key=="Keyword":
                rKeyword=data[simple_key]
                if rKeyword=="":
                    rKeyword={}
            elif simple_key=="Funding":
                rFunding=data[simple_key]
            elif simple_key=="Data":
                rData=data[simple_key]
            elif simple_key=="Method":
                rMethod=data[simple_key]
            else:
                print(simple_key)
                print("invalid data")
                sys.exit()

    qall="""
    create (j:JournalReference:Reference ) 
    set j=$rJournalReference
    merge(y:Year {name:$rYear.name}) 
    on create 
    set y=$rYear
    merge (jp:JournalPublication:Publication {publisherName:$rJournalPublication.publisherName}) 
    on create set jp=$rJournalPublication
    merge(p:Publisher {name:$rPublisher.name}) 
    on create  set p=$rPublisher
    create(f:Funding) set f=$rFunding
    create(d:Data) set d=$rData
    create(m:Method) set m=$rMethod
    create(j)-[:USED]->(d)
    create(j)-[:IN]->(y)
    create(j)-[:APPEARED_IN]->(jp)
    create(jp)-[:PUBLISHED_BY]->(p)
    create(j)-[:USED]->(m)
    create(jp)-[:USED]->(m)
    create(jp)-[:USED]->(d)
    create(j)<-[:FUNDED]-(f)
    """
    Dict_all={"rJournalReference":rJournalReference,"rYear":rYear,"rJournalPublication":rJournalPublication,
    "rPublisher":rPublisher,"rFunding":rFunding,"rData":rData,"rMethod":rMethod,
    "referenceTitle":referenceTitle,
    "referenceDOIURL":referenceDOIURL}

    complex_keys=[]
    for key in keys:
        if isinstance(data[key],list) and len(data[key])!=0:
            complex_keys.append(key)
    qauthor=""
    authors=[]
    qbib=""
    bibliographicReferences=[]
    qhyp=""
    hypothesiss=[]
    qprop=""
    propositions=[]
    qafiliation=""
    affiliations=[]
    qkey=""
    keywords=[]
    qcons=""
    constructs=[]

    for complex_key in complex_keys:
            if complex_key=="Author":
                authors=data[complex_key]
                qauthor="""
                UNWIND $authors as row
                create(a:Author) set a+=row;
                """
            elif complex_key=="BibliographicReference":
                bibliographicReferences=data[complex_key]           
                qbib="""
                UNWIND $bibliographicReferences AS row
                CREATE (b:BibliographicReference)
                SET b += row ;
                """
            elif complex_key=="Hypothesis":
                hypothesiss=data[complex_key]
                qhyp="""
                UNWIND $hypothesiss AS row
                create(h:Hypothesis) set h +=row;
                """

            elif complex_key=="Proposition":
                propositions=data[complex_key]
                qprop="""
                UNWIND $propositions AS row
                create(p:Proposition) set p+=row;
                """
            elif complex_key=="Affiliation":
                affiliations=data[complex_key]
                qafiliation="""
                unwind $affiliations as row
                create(af:Affiliation) set af+=row;
                """
            elif complex_key=="Keyword":
                keywords=data[complex_key]
                qkey="""
                unwind $keywords as row
                create(k:Keyword) set k+=row;
                """
            elif complex_key=="Construct":
                constructs=data[complex_key]
                qcons="""
                unwind $constructs as row
                create(c:Construct) set c+=row;
                """
            else:
                print(complex_key)
                print("invalid data")
                sys.exit()
    dict_complex={"authors":authors,
    "bibliographicReferences":bibliographicReferences,
    "hypothesiss":hypothesiss,
    "propositions":propositions,
    "affiliations":affiliations,
    "keywords":keywords,
    "constructs":constructs}
    query_all="""CALL apoc.cypher.runMany('""" + qauthor+ qbib + qhyp + qprop + qafiliation +qkey + qcons +"""',{authors:$authors,bibliographicReferences:$bibliographicReferences,hypothesiss:$hypothesiss,propositions:$propositions,affiliations:$affiliations,keywords:$keywords,constructs:$constructs},{statistics: false});"""


    Dict={"referenceDOI":referenceDOI,
    "authorScopusID":authorScopusID,
    "vPublisherName":vPublisherName,
    "referenceTitle":referenceTitle,
    "referenceDOIURL":referenceDOIURL}    


    q="""MERGE (iv:`Construct Role`:`Independent Variable`)
    MERGE (dv:`Construct Role`:`Dependent Variable`)
    MERGE (mv1:`Construct Role`:`Moderator Variable`)
    MERGE (mv2:`Construct Role`:`Mediator Variable`)
    MERGE (e:Empirical)
    MERGE (c:Conceptual)"""

    session.run (q,Dict)

    q="""CALL apoc.cypher.runMany('match(j:JournalReference)-[:USED]->(d:Data),
    (j)-[:APPEARED_IN]->(jp:JournalPublication),(jp)-[:PUBLISHED_BY]->(p:Publisher),
    (j)<-[:FUNDED]-(f:Funding),(a:Author),(b:BibliographicReference),(j)-[:USED]->(m:Method)
    where b.citingDOI = j.doi and (a.scopusID in j.authorScopusID ) and j.doi=$referenceDOI 
    merge (j)-[:AUTHORED_BY]->(a)
    merge (j)-[:CITED]->(b)
    MERGE (a)-[:CONTRIBUTED_TO]->(jp)
    MERGE (a)-[:CONTRIBUTED_TO]->(p)
    MERGE (a)-[:FUNDED_BY]->(f)
    MERGE (d)<-[r1:USED]-(a)
    set r1.referenceTitle=$referenceTitle, r1.referenceDOIURL=$referenceDOIURL
    MERGE (m)<-[r2:USED]-(a)
    set r2.referenceTitle=$referenceTitle, r2.referenceDOIURL=$referenceDOIURL;
    match(j:JournalReference)-[:AUTHORED_BY]->(a:Author),(af:Affiliation), (c:Construct)
    where  j.doi=$referenceDOI 
    and a.scopusID in af.authorScopusID and j.doi=c.doi 
    merge (j)-[:STUDIED]->(c)
    MERGE (jp)-[:STUDIED]->(c)
    merge (af)-[:PRODUCED]->(j);
    match(j:JournalReference)-[:AUTHORED_BY]->(a:Author),(h:Hypothesis),(j)-[:APPEARED_IN]->(jp:JournalPublication)
    where j.doi=$referenceDOI 
    and j.doi=h.doi 
    merge (j)-[:STUDIED]->(h)
    MERGE (jp)-[:STUDIED]->(h)
    MERGE (a)-[r:STUDIED]->(h)
    on match set r.referenceTitle=$referenceTitle, r.referenceDOIURL=$referenceDOIURL;
    match(j:JournalReference)-[:AUTHORED_BY]->(a:Author),(pr:Proposition),(j)-[:APPEARED_IN]->(jp:JournalPublication)
    where j.doi=$referenceDOI and j.doi=pr.doi 
    merge (jp)-[:STUDIED]->(pr)
    merge (a)-[r:STUDIED]->(pr)
    merge (j)-[:STUDIED]->(pr)
    on match set r.referenceTitle=$referenceTitle, r.referenceDOIURL=$referenceDOIURL;
    match(j:JournalReference)-[:AUTHORED_BY]->(a:Author),(k:Keyword)
    where j.doi=$referenceDOI 
    and k.doi=j.doi 
    merge (j)-[:HAS]->(k)
    MERGE (jp)-[:HAS]->(k)
    MERGE (a)-[r1:HAS]->(k)
    MERGE (p)-[:HAS]->(k)
    MERGE (a)-[r2:USED]->(k)
    on match set r1.referenceTitle=$referenceTitle, r1.referenceDOIURL=$referenceDOIURL,
    r2.referenceTitle=$referenceTitle, r2.referenceDOIURL=$referenceDOIURL;
    MATCH (c:Construct)<-[:STUDIED]-(j:JournalReference)-[:AUTHORED_BY]->(a:Author)
    where j.doi=$referenceDOI 
    MERGE (a)-[r:STUDIED]->(c)
    on match
    set r.referenceTitle=$referenceTitle, r.referenceDOIURL=$referenceDOIURL;
    MATCH (c:Construct)<-[:STUDIED]-(j:JournalReference)-[:STUDIED]->(h:Hypothesis)
    where j.doi=$referenceDOI and c.hypothesisID=h.hypothesisID
    MERGE (h)-[r:STUDIED]->(c)
    set r.referenceTitle=$referenceTitle, r.referenceDOIURL=$referenceDOIURL;
    MATCH (c:Construct)<-[:STUDIED]-(j:JournalReference)-[:STUDIED]->(p:Proposition)
    where j.doi=$referenceDOI and c.propositionID=p.propositionID
    MERGE (p)-[r:STUDIED]->(c)
    set r.referenceTitle=$referenceTitle, r.referenceDOIURL=$referenceDOIURL;
    MATCH (c:Construct), (iv:`Independent Variable`)
    WHERE c.ConstructRole = "IndependentVariable" and c.doi=$referenceDOI
    MERGE (c)-[:AS]->(iv);
    MATCH (c:Construct), (dv:`Dependent Variable`)
    WHERE c.ConstructRole = "DependentVariable" and c.doi=$referenceDOI
    MERGE (c)-[:AS]->(dv);
    MATCH (c:Construct), (mv:`Mediator Variable`)
    WHERE c.ConstructRole = "Mediator" and c.doi=$referenceDOI
    MERGE (c)-[:AS]->(mv);
    MATCH (c:Construct), (mv:`Moderator Variable`)
    WHERE c.ConstructRole = "Moderator" and c.doi=$referenceDOI
    MERGE (c)-[:AS]->(mv);
    match(j:JournalReference),(co:Conceptual)
    where  j.doi=$referenceDOI and j.isConceptual="True"
    merge (j)-[:HAS_TYPE]->(co);
    match(j:JournalReference),(em:Empirical)
    where  j.doi=$referenceDOI and j.isEmpirical="True"
    merge (j)-[:HAS_TYPE]->(em);
    ', {referenceDOI:$referenceDOI, referenceTitle:$referenceTitle,
    referenceDOIURL:$referenceDOIURL},{statistics: true});"""
    q_count="""MATCH (n:JournalReference)
    where n.doi= $referenceDOI RETURN tointeger(count(n)) as journal_count """
    count_run= session.run(q_count,Dict)
    journal_count=[{"journal_count": row["journal_count"]} for row in count_run]
    journal_count=(journal_count[0]['journal_count'])  
    startTime = time.perf_counter()
    if (journal_count<1):
        try:       
            session.run(qall,Dict_all)
            session.run(query_all,dict_complex)
            session.run (q,Dict)
        except Exception as e:
            print(str(e))
            request_time = time.perf_counter() - startTime
            logger.info("Request completed in {0:.0f}ms".format(request_time))
        return ({"status":"ok"})
    else:
        return ({"journal reference already exists":"ok"}) 


def setup_custom_logger(name):
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    handler = logging.FileHandler('log.txt', mode='w')
    handler.setFormatter(formatter)
    screen_handler = logging.StreamHandler(stream=sys.stdout)
    screen_handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.addHandler(screen_handler)
    return logger
