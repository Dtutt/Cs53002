def ratree(Ra):
    i=0
    #Keep Track of brackets and parenthese
    openpar=False
    openbracket=True
    section=[""]
    #checking char by char
    #creating sections based on [] or () where [] holds higher priority
    for char in Ra:
        #check for Parentehse Open
        if char=='(':
            section[i]+=char
            openpar=True
        #check for Paranethese close
        elif char ==')':
            section[i]+=char
            openpar=False
            # if not withing a [] new section
            if not openbracket:
                section.append("")
                i+=1
        #check for bracket opening
        elif char=='[':
            section[i]+=char
            openpar=True
        #check for bracket close
        elif char ==']':
            section[i]+=char
            openpar=False
            section.append("")
            i+=1

        else:
            section[i]+=char
    i=0
    #simple print because current features won't have branches
    while i+1 <section.__len__():
        print(section[i])
        if i+2 != section.__len__():
            for x in range(0,3):
                print(' |')
            print('\/')
        i+=1
    return section

