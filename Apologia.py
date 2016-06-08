__module_name__,__module_version__=("Apologia","0.9.0")
__module_description__="A hexchat script for displaying and searching bible texts"
print("\0034"+__module_name__+" "+__module_version__+" loaded\003")
import collections,re,string,threading,time,xchat
print(time.ctime()+" loading versions ... ")
###
# module variables
###
cmdc="!"
fileName="./Apologia/resources/<n>.properties"
split,strip,upper=(str.split,str.strip,str.upper)
OrderedDict,Thread=(collections.OrderedDict,threading.Thread)
join,lower,replace=(str.join,str.lower,str.replace,)
bold,red,underline=("\002","\0034","\010")
versions={}
###
# get bible book names and then version names
###
bookName,versionName=(OrderedDict(),OrderedDict())
bn=replace(fileName,"<n>","Biblebooks")
with open(bn,"r") as booksFile:
	for line in booksFile:
		k,n=split(line,"=")
		n=replace((replace(n,"\r","")),"\n","")
		bookName[k]=n
vn=replace(fileName,"<n>","BibleVersions")
with open(vn,"r") as versionsFile:
	for line in versionsFile:
		k,n=split(line,"=")
		n=replace((replace(n,"\r","")),"\n","")
		versionName[k]=n
###
# helper functions
###
def displayPassage(version,book,ref,xcContext):
	reflist=decodeRef(ref)
	chapter=reflist[0]
	first,last=(0,0)
	try:
		if len(reflist)==2: first,last=(int(reflist[1]),int(reflist[1]))
		elif len(reflist)==3: 
			first,last=(int(reflist[1]),int(reflist[2]))
			if last<=first: last=first
		else:
			say("passage reference: "+bold+ref+bold+" is incorrect",xcContext)
			return 
	except:
		say("passage reference: "+bold+ref+bold+" is incorrect",xcContext)
		return
	keylist=[]
	if lower(book) in ["ccc","cct"]: last=first # allow only one CCC verse
	if (last-first)>3: last=first+3
	for i in range(first,last+1):
		s=book+chapter+"_"+str(i)
		keylist.append(s)
	verses=versions[version]
	for k in keylist:
		try:
			ref=refExpander(k)
			say(bold+ref+bold+" "+verses[k],xcContext)
		except:
			say("I could not find "+bold+refExpander(k)+bold,xcContext)
def searchVersion(version,phrase,xcContext):
	ss=""
	verses,foundVerses=(versions[version],OrderedDict())
	i,max=(0,20)
	###
	# search by set of words
	###
	if (strip(phrase)[0]) in ("[","{","("):
		s,b=("[{()}]","      ")
		table=string.maketrans(s,b)
		sp=strip(string.translate(phrase,table))
		sp=lower(removePunctuation(sp))
		swords=set(split(sp," "))
		wc=len(swords)
		for k in verses:
			verse=lower(removePunctuation(verses[k]))
			vwords=set(split(strip(verse)))
			if swords.issubset(vwords):
				i=i+1
				if i>max: break # stop reading verses
				foundVerses[k]=verses[k]
				ref=refExpander(k)
				if i==1: ss="found in "+version+": "+ref
				else: ss=ss+", "+ref
	###
	# search by phrase
	###
	else:
		rePhrase=r"\b"+lower(phrase)+r"\b"
		for k in verses:
			verse=verses[k]
			foundlist=re.findall(rePhrase,lower(removePunctuation(verse)))
			if len(foundlist)>0:
				foundVerses[k]=verses[k]
				i=i+1
				if i>max: break # stop reading verses
				ref=refExpander(k)
				if i==1: ss="found in "+version+": "+ref
				else: ss=ss+", "+ref
	###
	# send search information back to the context from which the request came
	###
	if i>max: 
		say(ss+" ... more than 20found",xcContext)
		return 
	if i==0: 
		say("I did not find any occurence of: "
		+bold+phrase+bold+" in version: "+version,xcContext)
		return 
	say(ss,xcContext) # say what was found
	if i<5: # say the results if 4 or less were found
		for fk in foundVerses: 
			say(bold+refExpander(fk)+bold+" "+foundVerses[fk],xcContext)
			if lower(version) in ["ccc","cct"]: 
				say(red+"because "+version
				+" sections are large only one is displayed",xcContext)
				break
###
# utility functions
###
def decodeRef(ref):
	s=".,:;-_"
	b="      "
	table=string.maketrans(s,b)
	r=string.translate(ref,table)
	return split(r)
def getVersion(version):
	bv=OrderedDict()
	bn=replace(fileName,"<n>",strip(version))
	try:
		with open(bn,"r") as properties:
			for line in properties:
				v=split(line,"=")
				k=strip(v[0])
				t=replace(v[1],"\r","")
				t=replace(t,"\n","")
				bv[k]=strip(t)
			return bv
	except:
		bv["error"]="I could not find version "+bold+version+bold
		return bv
def refExpander(ref):
	book=ref[:3]
	bName=bookName[book]
	chapter=split(ref[3:],"_")[0]+":"
	verse=split(ref[4:],"_")[1]
	if bName in ["CCC","CCT"]: chapter=""
	r = bName+" "+chapter+verse
	return r
def removePunctuation(s):
	table=string.maketrans("","")
	return s.translate(table,string.punctuation)
def say(ss,xcContext):
	if len(ss)<350: xcContext.command("SAY "+ss)
	else:
		while len(ss)>300:
			pos=ss.find(" ",300,)
			if pos!=-1:
				ssp=ss[:pos]
				ss=ss[pos+1:]
			else:
				ssp=ss[:300]
				ss=ss[300:]
			xcContext.command("SAY "+ssp)
		xcContext.command("SAY "+ss)
###
# callback functions
###
def parseChannelMessage(word,word_eol,userdata):
	xcContext=xchat.get_context()
	sender,message=(word[0],join(" ",split(word[1])))
	firstchar=message[0]
	if firstchar==cmdc:
		cmd=split(message[1:]," ")
		firstpart=lower(cmd[0])
		if firstpart=="versions":
			ss=""
			for k in versionName:
				ss=ss+bold+k+bold+"("+versionName[k]+") "
			say("SAY "+ss,xcContext)
			return 
		if firstpart=="help":
			say("To display a passage type "+bold+";rsv John 3:16"+bold
			+" all bible book names are abbreviated to their first 3"
			+" letters, for example 1Kings is 1ki, John is joh, and so forth."
			+" There are exceptions: Judges is "+bold+"jdg,"+bold
			+" Judith is "+bold+"jdt"+bold+", and Philemon is "
			+bold+"phm"+bold,xcContext)
			say("Searching is done by putting a 's' in front of the"
			+" version name like this "+bold+";skjv God so loved"+bold
			+" that will find all the verses in the KJV containing"
			+" 'God so loved'",xcContext)
			say("To display versions type "+bold+";versions"+bold,xcContext)
			return 
		if firstpart[0]=="s": 
			version=upper(firstpart[1:])
			if version not in versionName: return
			phrase=lower(join(" ",cmd[1:]))
			Thread(target=searchVersion,args=(version,phrase,xcContext)).start()
		else:
			if len(cmd)<3:
				if len(cmd)==2:
					if upper(cmd[0]) in ["CCC","CCT"]:
						version=book=upper(cmd[0])
						ref="1_"+removePunctuation(cmd[1])
						Thread(target=displayPassage,args=(version,book,ref,xcContext)).start()
			elif len(cmd)==3: 
				version=upper(cmd[0])
				if version not in versionName: return
				book=upper(cmd[1])
				if book in ["JUDGES","JUDG"]: book="JDG"
				elif book in ["JUDITH", "JUDI"]: book="JDT"
				elif book in ["PHILEMON","PHL"]: book="PHM"
				elif book in ["RUTH","RUT"]: book="RTH"
				bref=book[:3]
				ref=cmd[2]
				Thread(target=displayPassage,args=(version,bref,ref,xcContext)).start()
###
# get versions
###
for k in versionName: 
	versions[k]=getVersion(k)
print(time.ctime()+" finished loading")
###
# hooks
###
xchat.hook_print("Channel Message", parseChannelMessage)
xchat.hook_print("Private Message to Dialog", parseChannelMessage)