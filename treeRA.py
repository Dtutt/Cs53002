from anytree import Node, RenderTree

def ratree(Ra):
    i=0
    #Keep Track of brackets and parenthese
    openpar=0
    openbracket=0
    section=[""]
    #checking char by char
    #creating sections based on [] or () where [] holds higher priority
    for char in Ra:
        #check for Parentehse Open
        if char=='(':
            section[i]+=char
            openpar+=1
        #check for Paranethese close
        elif char ==')':
            section[i]+=char
            openpar-=1
            # if not withing a [] new section
            if openbracket==0:
                section.append("")
                i+=1
        #check for bracket opening
        elif char=='[':
            section[i]+=char
            openbracket+=1
        #check for bracket close
        elif char ==']':
            section[i]+=char
            openbracket-=1
            section.append("")
            if openbracket==0:
                section.append("")
                i+=1

        else:
            section[i]+=char
    i=0
    section=list(filter(None,section))
    #simple print because current features won't have branches
    root=ratree2(section)
    for pre, fill, node in RenderTree(root):
        print("%s%s" % (pre, node.name))
    return root

def ratree2(section):
    i=0
    nodes=[]
    parent=None
    while i<section.__len__():
        nodes.append(Node(section[i],parent=parent))
        parent=nodes[i]
        i+=1
    return nodes[0]