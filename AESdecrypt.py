from AESdecryptfunc import * #import AESdecryptfunc module to use functions created for this program
import math #import math module to use function such as ceiling
import io
import scrypt

#check that script is running with the two text files as the two parameters or else quit
if len(sys.argv) is not 3:#takes in two arguments for the ciphertext.txt file name and plainhex.txt file name
    sys.exit("Error, script needs two command-line arguments. (Ciphertext.txt File and plainhex.txt File)")

PassPhrase=""
def string2bits(par=""):
    return [bin(ord(x))[2:].zfill(8) for x in par]
def xor_two_str(a,b):
    return ''.join([hex(ord(a[i%len(a)]) ^ ord(b[i%(len(b))]))[2:] for i in range(max(len(a), len(b)))])

def Master_Key_128(K1,K2):
    #Key Mixing-Start
    K1_1=string2bits(K1)[0:8]
    K1_2=string2bits(K2)[8:16]
    K2_1=string2bits(K2)[0:8]
    K2_2=string2bits(K2)[8:16]
    result=[]
    for i in range(8):
        result.append(xor_two_str(K2_1[i],xor_two_str(K1_1[i],xor_two_str(K1_2[i],K2_2[i]))))
    #Key Mixing-End
    #Key Expansion-Start
    K1_1_result=''.join(i for i in K1_1)
    K1_2_result=''.join(i for i in K1_2)
    K2_1_result=''.join(i for i in K2_1)
    K2_2_result=''.join(i for i in K2_2)
    temp=""

    for i in range(1,17):
        temp=temp+"".join(K1_1_result[4*i-1])+"".join(K1_2_result[4*i-1])+"".join(K2_1_result[4*i-1])+"".join(K2_2_result[4*i-1])

    for i in range(8):
        result.append(("".join(j for j in list(temp)[8*i:8*i+8])))
    #KeyExpansion-End
    #Converting Final Key into characters from binary
    finalkey=''
    for i in range(16):
        if(int(result[i],2)<32):
            finalkey=finalkey+chr(int(result[i],2)+33)
        else:
            finalkey=finalkey+chr(int(result[i],2))

    salt = 'd7d42612c5ff4625'
    hashed_key=scrypt.hash(finalkey,salt)
    return [finalkey,hashed_key]


K1=input("Enter K1: ")
K2=input("Enter K2: ")
print("\n")
k=Master_Key_128(K1,K2)
print("Hashed Key using Scrypt",k[1])
print("\n")

while(len(PassPhrase)!=16):
    print("Enter in the 16 character passphrase to decrypt your text file %s" %sys.argv[1])
    PassPhrase=k[0] #takes in user input of char, eg. "Iwanttolearnkung"
    if(len(PassPhrase)<16):#check if less than 16 characters, if so add one space character until 16 chars
        while(len(PassPhrase)!=16):
            PassPhrase=PassPhrase+"\00"
    if(len(PassPhrase)>16):#check if bigger than 16 characters, if so then truncate it to be only 16 chars from [0:16]
        print("Your passphrase was larger than 16, truncating passphrase.")
        PassPhrase=PassPhrase[0:16]

#open ciphertext.txt file to read and decrypt
file=open(sys.argv[1], "r")
message=(file.read())
print("Inside your ciphertext message is:\n%s\n" % message)
file.close()

#set up some parameters
start=0#set starting pointer for the part to decrypt of the ciphertext
end=32#set ending pointer for the part to decrypt of the plaintex
length=len(message)#check the entire size of the message
loopmsg=0.00#create a decimal value
loopmsg=math.ceil(length/32)+1#use formula to figure how long the message is and how many 16 character segmentss must be decrypted
outputhex=""#setup output message segment in hex
asciioutput=""#setup compilation of output message in ascii

#need to setup roundkeys here
PassPhrase=BitVector(textstring=PassPhrase)
roundkey1=findroundkey(PassPhrase.get_bitvector_in_hex(),1)
roundkey2=findroundkey(roundkey1,2)
roundkey3=findroundkey(roundkey2,3)
roundkey4=findroundkey(roundkey3,4)
roundkey5=findroundkey(roundkey4,5)
roundkey6=findroundkey(roundkey5,6)
roundkey7=findroundkey(roundkey6,7)
roundkey8=findroundkey(roundkey7,8)
roundkey9=findroundkey(roundkey8,9)
roundkey10=findroundkey(roundkey9,10)
roundkeys=[roundkey1,roundkey2,roundkey3,roundkey4,roundkey5,roundkey6,roundkey7,roundkey8,roundkey9,roundkey10]

FILEOUT = io.open(sys.argv[2], 'w', encoding='utf-8')

# set up the segement message loop parameters
for y in range(1, loopmsg): # loop to encrypt all segments of the message
    plaintextseg = message[start:end]

    # add round key
    bv1 = BitVector(hexstring=plaintextseg)
    bv2 = BitVector(hexstring=roundkeys[9])
    resultbv = bv1 ^ bv2
    myhexstring = resultbv.get_bitvector_in_hex()

    #inverse shift row
    myhexstring=invshiftrow(myhexstring)

    #inverse subbyte
    myhexstring=invsubbyte(myhexstring)

    for x in range(8, -1, -1):
        # add roundkey for current round
        bv1 = BitVector(hexstring=myhexstring)
        bv2 = BitVector(hexstring=roundkeys[x])
        resultbv = bv1 ^ bv2
        myhexstring = resultbv.get_bitvector_in_hex()

        # mix column
        bv3 = BitVector(hexstring=myhexstring)
        myhexstring=invmixcolumn(bv3)

        # shift rows
        myhexstring = invshiftrow(myhexstring)

        # sub byte
        myhexstring = invsubbyte(myhexstring)

    #add initial round key
    bv1 = BitVector(hexstring=myhexstring)
    bv2 = PassPhrase
    resultbv = bv1 ^ bv2
    myhexstring = resultbv.get_bitvector_in_hex()

    start = start + 32 #increment start pointer
    end = end + 32 #increment end pointer

    replacementptr = 0
    while (replacementptr < len(myhexstring)):
        if (myhexstring[replacementptr:replacementptr + 2] == '0d'):
            myhexstring = myhexstring[0:replacementptr] + myhexstring[replacementptr+2:len(myhexstring)]
        else:
            replacementptr = replacementptr + 2

    outputhex = BitVector(hexstring=myhexstring)
    asciioutput = outputhex.get_bitvector_in_ascii()
    asciioutput=asciioutput.replace('\x00','')
    FILEOUT.write(asciioutput)

FILEOUT.close()

file2=io.open(sys.argv[2], "r", encoding='utf-8')
print("The decrypted message for the entire ciphertext is:\n%s\n" % file2.read())
file2.close()
