__module_name__,__module_version__=("WordWrap","1.0.0")
__module_description__="Xchat message word-wrap for longer messages"
print("\0034"+__module_name__+" "+__module_version__+"loaded\003")
import xchat
###
# callback functions
###
def wordWrap(command,word,word_eol,userdata):
    if len(word_eol[0])<350: return
    ss=word_eol[0].strip(" ")
    while len(ss)>300:
        pos=ss.find(" ",300,)
        if pos!=-1:
            ssp=ss[:pos+1]
            ss=ss[pos:]
        else:
            ssp=ss[:300+1]
            ss=ss[300:]
        xchat.command("SAY "+ssp)
    xchat.command("SAY "+ss)
    return xchat.EAT_ALL
def processSAY(word,word_eol,userdata):
    return wordWrap("SAY",word,word_eol,userdata)
def processME(word,word_eol,userdata):
    return wordWrap("ME",word,word_eol,userdata)
###
# hooks
###
xchat.hook_command("",processSAY)
xchat.hook_command("SAY",processSAY)
xchat.hook_command("ME",processME)
xchat.hook_command("MSG",processSAY)
