# -*- coding: utf-8 -*-
#!/usr/bin/python

from random import getrandbits
from random import randint
from hashlib import sha224
import re
import os.path
import os
import math
import sys

# ============================================ Funções ============================================  #

# @Brief Exponenciação modular
# @Arg1 -> Base a ser testada
# @Arg2 -> Expoente da base
# @Arg3 -> Valor do módulo
# @Arg4 -> Resto (padrão/inicial
# @Return -> Resultado da exponenciação modular
def expMod(base, exp, mod):
    rest = 1
    while exp:
        if exp & 1:
            rest = rest * base % mod
        exp >>= 1
        base = base * base % mod
    return rest

# @Brief MDC
# @Arg1 -> Dividendo
# @Arg2 -> Divisor
# @Return -> MDC(dividendo, divisor)
def mdc(a, b):
    if b == 0:
        return a
    else:
        return mdc(b, a % b)

# @Brief Teste de Miller Rabin
# @Arg1 -> Número a ser testado.
# @Arg2 -> Base a ser utilizada par ao teste (padrão = 2).
# @Return -> True se Composto ou False se Pseudoprimo.
def millerRabinUnitTest(n, b = 2):
    assert(n >= 2)
    k = 0
    q = n - 1
    while q % 2 == 0:
        k = k + 1
        q = q/2
    t = expMod(b, q, n)
    if t == 1 or t == (-1 % n):
        return False
    for i in range(0, k):
        t = expMod(t, 2, n)
        if t == n - 1:
            return False
    return True

# @Brief Realiza o teste de Miller Rabin para diversas.
# @Arg1 -> Número a ser testado.
# @Arg2 -> Quantidade de bases para testar (padrão = 10).
# @Return -> False se composto ou True se PseudoPrimo.
def millerRabinMultiTest(n, bases = 30):
    assert(n >= 2)
    if bases > n:
        b = bases - n
    usedBases = []
    for i in range(0, 10):
        b = randint(2, n-1)
        while (b in usedBases):
            b = randint(2, n-1)
        usedBases.append(b)
        if millerRabinUnitTest(n, b):
            return False
    return True

# @Brief Retorna um número possívelmente primo
# @Arg1 -> Tamanho, em bits, do primo a ser gerado (padrão = 128)
# @Return -> Um possível número primo de tamanho igual ao seu argumento
def generatePossiblePrime(bits = 128):
    possiblePrimeNumber = getrandbits(bits) 
    while not millerRabinMultiTest(possiblePrimeNumber):
        possiblePrimeNumber = getrandbits(bits)
    return possiblePrimeNumber

# @Brief Obtém o inverso de b módulo n
# @Arg1 -> Primo
# @Arg2 -> Primo
# @Return -> Inverso de b módulo n
def getInverse(b, n):
    x0, x1, y0, y1 = 1, 0, 0, 1
    while n != 0:
        q, b, n = b // n, n, b % n
        x0, x1 = x1, x0 - q * x1
        y0, y1 = y1, y0 - q * y1
    assert(b == 1)
    return x0

# @Brief Verifica se b tem inverso módulo n
# @Arg1 -> Primo
# @Arg2 -> Primo
# @Return -> True se MDC(arg1,arg2)=1 ou False se MDC(arg1, arg2)!=1  
def hasInverse(b, n):
    x0, x1, y0, y1 = 1, 0, 0, 1
    while n != 0:
        q, b, n = b // n, n, b % n
        x0, x1 = x1, x0 - q * x1
        y0, y1 = y1, y0 - q * y1
    if b == 1:
        return True
    return False

# @Brief Realiza uma leitura fragmentada e sob demanda de uma arquivo
# @Arg1 -> Delimitador para leitura fragmentada
# @Arg2 -> Tamanho do buffer
# @Return -> Fragmento do texto lido
def fileSplit(f, delimeter = '-', bufsize = 1024):
    frag = ''
    while True:
        s = f.read(bufsize)
        if not s:
            break
        split = s.split(delimeter)
        if len(split) > 1:
            yield frag + split[0]
            frag = split[-1]
            for x in split[1:-1]:
                yield x
        else:
            frag += s
    if frag:
        yield frag

def convertToHex(decimal):
    n = (decimal % 16)
    temp = ""
    if (n < 10):
        temp = n
    if (n == 10):
        temp = "A"
    if (n == 11):
        temp = "B"
    if (n == 12):
        temp = "C"
    if (n == 13):
        temp = "D"
    if (n == 14):
        temp = "E"
    if (n == 15):
        temp = "F"
    if (decimal - n != 0):
        return convertToHex(decimal / 16) + str(temp)
    else:
        return str(temp)
    
def convertToDec(hexadecimal):
	n = hexadecimal
	result = int(n,16)
	return str(result)
        
# @Brief Realiza uma leitura completa de um arquivo
# @Arg1 -> Nome/Caminho do arquivo
# @Return -> Conteúdo do arquivo
def readAllFile(path):
    with open(path, 'rb') as f:
        return f.read()
    
# @Brief Verifica se um arquivo existe
# @Arg1 -> Nome/Caminho do arquivo
# @Return -> True ou False
def isThisFileExists(path):
    return os.path.isfile(path)

# @Brief Pergunta ao usuário se ele deseja salvar as chaves num arquivo
# @Return -> True ou False
def makeQuestion(message):
    print ""
    print message + "(s/n)"
    ans = raw_input()
    while not (ans != 's' or ans != 'n'):
            ans = raw_input()
    if ans == 's':
        return True
    return False

def changeNameExtensionsToDotKryptos(path):
    return path.rpartition('.')[0] + ".txt"

def getKeysFromFile(path):
    content = readAllFile(path)
    values = []
    for i in re.findall(r'\w*[0-9A-F]', content):
        values.append(int(convertToDec(i)))
    print values
    return values
    
    


# ============================================= RSA =============================================  #

# @Brief Encontra o valor da chave pública "e" do RSA
# @Arg1 -> fiN
# @Return -> Chave pública (e)
def getKeyE(fiN):
    e = 2
    while not hasInverse(e, fiN):
        e = e +1
    return e

# @Brief Encontra o valor da chave privada "d" do RSA
# @Arg1 -> Chave pública e do RSA
# @Arg2 -> fiN
# @Return -> Chave privada (d)
def getKeyD(e, fiN):
    return getInverse(e,fiN) % fiN

# @Brief Calcula as chaves (públicas e privadas) do RSA 
# @Arg1 -> Primo de 128 bits de tamanho
# @Arg2 -> Primo de 128 bits de tamanho
# @Return -> Chaves (públicas e privadas) do RSA (n, e, d)
def keysRSA(p, q):
    n = p * q
    fiN = (p-1) * (q-1)
    e = getKeyE(fiN)
    d = getKeyD(e, fiN)
    return n, e, d

# @Brief Encripta um bloco de bytes utilizando o RSA
# @Arg1 -> Bloco, em bytes, a ser encriptado (char)
# @Arg2 -> Primeiro componente da chave pública (n)
# @Arg3 -> Segundo componente da chave pública (e)
# @Return -> Retorna o bloco de bytes encriptado (int)
def encryptionRSA(toEncrypt, n, e):
    return expMod(toEncrypt, e, n)

# @Brief Decripta um bloco de bytes utilizando o RSA
# @Arg1 -> Valor a ser decriptado (int)
# @Arg2 -> Primeiro componente da chave privada (n)
# @Arg3 -> Segundo componente da chave privada (d)
# @Return -> Retorna o valor decriptado (char)
def decryptionRSA(toDecrypt, n, d):
    return expMod(toDecrypt, d, n)

# ============================================ El Gamal ============================================  #

# @Brief Gera um primp P e o gerador G (sem gauss) para o método El Gamal
# @Arg1 -> tamanho do número Q que gerará P e G
# @Return -> Retorna um Primo P e um gerador G
def generatePrimeAndGeneratorToElGamal(bits = 255):
    q = getrandbits(bits) 
    while True:
        while not millerRabinMultiTest(q):
            q = getrandbits(bits)
        p = 2*q + 1
        if millerRabinMultiTest(p):
            break
        q = getrandbits(bits)
    g = 2
    while expMod(g, q, p) == 1:
        g = g + 1
    return p, g

# @Brief Gera todas as chaves necessárias para o método El Gamal
# @Return -> Retorna chaves para o método El Gamal
def keysElGamal():
    p, g = generatePrimeAndGeneratorToElGamal()
    d = randint(2, p-2)
    c = expMod(g, d, p)
    return p, g, c, d

# @Brief Encripta um bloco de bytes utilizando o El Gamal
# @Arg1 -> Bloco, em bytes, a ser encriptado
# @Arg2 -> Chave pública (p)
# @Arg3 -> Chave pública (g)
# @Arg4 -> Chave pública (c)
# @Return -> Retorna o bloco de bytes encriptado no formato tuple
def encryptionElGamal(toEncrypt, p, g, c):
    k = randint(2, 10) # Explicar isso
    s = expMod(g, k, p)
    t = (toEncrypt * pow(c,k)) % p
    return (s, t)

# @Brief Decripta um bloco de bytes utilizando o El Gamal
# @Arg1 -> Bloco (s,t) a ser decriptado no formato tuple
# @Arg2 -> Chave privada (p)
# @Arg3 -> Chave privada (d)
# @Return -> Retorna o bloco de bytes decriptado.
def decryptionElGamal(toDecrypt, p, d): #toDecrypt = (s, t)
    s = expMod(getInverse(toDecrypt[0], p), d , p)
    return s * toDecrypt[1] % p

# =========================================== Signature ===========================================  #

def signature(filename, p, g, a):

    #Encontrando um K que possua inverso módulo p-1
    k = randint(2,p-2)
    while mdc(k, p-1) != 1:
        k = randint(2,p-2)

    #Calculando o inverso de K
    ki = getInverse(k, p-1) % (p-1)
    
    arq = open(filename, 'rb')
    # Pegando o hash da mensagem em formato hexadecimal...
    content = arq.read()
    h = int(sha224(content).hexdigest(), 16)

    # Calculando R
    r = expMod(g, k, p)

    # Calculando S
    s = (ki * (h - a*r)) % (p-1)

    # Retornando a assinatura R e S
    return (r, s)
    

def checkSignature(filename, signature, p, g, v):

    # Separando as variáveis R e S que estão em Signature
    r = signature[0]
    s = signature[1]

    # Verificando se R está entre 1 e p-1
    if r < 1 or r > p-1:
        return False
    
    arq = open(filename, 'rb')
    # Pegando o hash da mensagem em formato hexadecimal...
    content = arq.read()
    h = int(sha224(content).hexdigest(), 16)

    # Calculando u1 e u2
    # No livro o cálculo possui a seguinte forma:
    # ( pow(v,r) * pow(r,s) ) % p
    # Mas dessa forma o programa "voa"
    print ("p", p)
    print ("v", v)
    print ("r", r)
    print ("s", s)
    print ("h", h)
    u1 = (expMod(v, r, p) * expMod(r, s, p)) % p
    u2 = expMod(g, h, p)

    print ("u1", u1)
    print ("u2", u2)

    # Verificando u1 e u2 são diferentes 
    if u1 != u2:
        return False

    return True

    

# ========================================== Main methods =========================================  #

def encryption(encryptionMethod, filenameToEncrypt):
    fileToEncrypt = open(filenameToEncrypt, "rb")
    fileEncrypted = open( "E" + fileToEncrypt.name, "w")
    if encryptionMethod == "rsa":
        n, e, d = keysRSA(generatePossiblePrime(), generatePossiblePrime())
        print "\nChaves criptográficas:"
        print "\tn = %s" % convertToHex(n)
        print "\te = %s" % convertToHex(e)
        print "\td = %s" % convertToHex(d)
        if makeQuestion("Gostaria de salvar as chaves em um arquivo?"):
            keysFile = open("keys-" + encryptionMethod + "-" + changeNameExtensionsToDotKryptos(fileEncrypted.name), "w")
            keysFile.write("n - %s\n" % convertToHex(n))
            keysFile.write("e = %s\n" % convertToHex(e))
            keysFile.write("d = %s\n" % convertToHex(d))
            print "\nArquivo salvo com o nome %s" % (keysFile.name)
        byte = fileToEncrypt.read(1)
        byteEncripted = 0
        while byte != "":
            byteEncrypted = encryptionRSA(ord(byte), n, e)
            fileEncrypted.write("%ld" % long(byteEncrypted))
            fileEncrypted.write("-")
            byte = fileToEncrypt.read(1)
    elif encryptionMethod == "elgamal":
        p, g, c, d = keysElGamal()
        print "\nChaves criptográficas:"
        print "\tp = %s" % convertToHex(p)
        print "\tg = %s" % convertToHex(g)
        print "\tc = %s" % convertToHex(c)
        print "\td = %s" % convertToHex(d)
        if makeQuestion("Gostaria de salvar as chaves em um arquivo?"):
            keysFile = open("keys-" + encryptionMethod + "-" + changeNameExtensionsToDotKryptos(fileEncrypted.name), "w")
            keysFile.write("p - %s\n" % convertToHex(p))
            keysFile.write("g = %s\n" % convertToHex(g))
            keysFile.write("c = %s\n" % convertToHex(c))
            keysFile.write("d = %s\n" % convertToHex(d))
            print "\nArquivo salvo com o nome %s" % (keysFile.name)
        byte = fileToEncrypt.read(1)
        byteEncripted = 0
        while byte != "":
            byteEncrypted = encryptionElGamal(ord(byte), p, g, c)
            fileEncrypted.write("%ld" % long(byteEncrypted[0]))
            fileEncrypted.write("|")
            fileEncrypted.write("%ld" % long(byteEncrypted[1]))
            fileEncrypted.write("-")
            byte = fileToEncrypt.read(1)

def decryption(decryptionMethod, fileToDecrypt):
    fileDecrypted = open( "D" + fileToDecrypt, "wb")
    if decryptionMethod == "rsa":
        if makeQuestion("Gostaria de digitar as chaves em vez de selecionar o arquivo?"):
            print "Insira a chave decriptográfica n:"
            n = int(convertToDec(raw_input()))
            print "insira a chave decriptográfica d:"
            d = int(convertToDec(raw_input()))
        else:
            print "\nPor favor, insira o nome do arquivo"
            keysFile = raw_input()
            while not isThisFileExists(keysFile):
                print "\nArquivo inexistente!"
                print "Insira o nome correto do arquivo ou apert \"Ctrl + C\" para encerrar o programa"
                keysFile = raw_input()
            keys = getKeysFromFile(keysFile)
            assert(len(keys) == 3)
            n = keys[0]
            d = keys[2]
            print "\nChaves decriptográficas encontras:"
            print "\tn = %s" % convertToHex(n)
            print "\td = %s" % convertToHex(d)
        print "\nIniciando decriptação"
        for i in fileSplit(open(fileToDecrypt)):
            fileDecrypted.write(chr(decryptionRSA(int(i), n, d)))
    elif decryptionMethod == "elgamal":
        if makeQuestion("Gostaria de digitar as chaves em vez de selecionar o arquivo?"):
            print "Insira a chave decriptográfica p:"
            p = int(convertToDec(raw_input()))
            print "insira a chave decriptográfica d:"
            d = int(onvertToDec(raw_input()))
        else:
            print "\nPor favor, insira o nome do arquivo"
            keysFile = raw_input()
            while not isThisFileExists(keysFile):
                print "\nArquivo inexistente!"
                print "Insira o nome correto do arquivo ou apert \"Ctrl + C\" para encerrar o programa"
                keysFile = raw_input()
            keys = getKeysFromFile(keysFile)
            assert(len(keys) == 4)
            p = keys[0]
            d = keys[3]
            print "\nChaves decriptográficas encontras:"
            print "\tp = %s" % convertToHex(p)
            print "\td = %s" % convertToHex(d)
        print "\nIniciando decriptação"
        for i in fileSplit(open(fileToDecrypt)):
            itupled = i.split("|")
            it = []
            it.append(int(itupled[0]))
            it.append(int(itupled[1]))
            fileDecrypted.write(chr(decryptionElGamal(it, p, d)))
    print "\nNome do arquivo %s" % (fileDecrypted.name)

def signatureFile(filename, method):
    if method == "sign":
        print "\nGerando chaves de assinatura..."
        p, g, v, a = keysElGamal()
        print "\nChaves de assinagura digital:"
        print "\tp = %s" % convertToHex(p)
        print "\tg = %s" % convertToHex(g)
        print "\tv = %s" % convertToHex(v)
        print "\ta = %s" % convertToHex(a)
        if makeQuestion("Gostaria de salvar as chaves em um arquivo?"):
            keysFile = open("keys-signature-" + changeNameExtensionsToDotKryptos(filename), "w")
            keysFile.write("p - %s\n" % convertToHex(p))
            keysFile.write("g = %s\n" % convertToHex(g))
            keysFile.write("v = %s\n" % convertToHex(v))
            keysFile.write("a = %s\n" % convertToHex(a))
            print "\nArquivo salvo com o nome %s" % (keysFile.name)
        digSign = signature(filename, p, g, a)
        print "\nA assinatura digital do arquivo %s é o par:"
        print "r = %s\n" % convertToHex(digSign[0])
        print "s = %s\n" % convertToHex(digSign[1])
        if makeQuestion("Gostaria de salvar a assinatura em arquivo?"):
            digSignFile = open("signature-" + changeNameExtensionsToDotKryptos(filename), "w")
            digSignFile.write("r = %s\n" % convertToHex(digSign[0]))
            digSignFile.write("s = %s\n" % convertToHex(digSign[1]))
            print "\nNome do arquivo contendo o par da assinatura é %s" % (digSignFile.name)
        print "\nAssinatura concluída"
    else:
        if makeQuestion("Gostaria de digitar as chaves em vez de selecionar o arquivo?"):
            print "Insira a chave de assinatura p:"
            p = int(convertToDec(raw_input()))
            print "insira a chave de assinatura g:"
            g = int(convertToDec(raw_input()))
            print "insira a chave de assinatura v:"
            v = int(convertToDec(raw_input()))		    
        else:
            print "\nPor favor, insira o nome do arquivo"
            keysFile = raw_input()
            while not isThisFileExists(keysFile):
                print "\nArquivo inexistente!"
                print "Insira o nome correto do arquivo ou apert \"Ctrl + C\" para encerrar o programa"
                keysFile = raw_input()
            keys = getKeysFromFile(keysFile)
            assert(len(keys) == 4)
            p = keys[0]
            g = keys[1]
            v = keys[2]
            print "\nChaves de assinatura encontradas:"
            print "\tp = %s" % convertToHex(p)
            print "\tg = %s" % convertToHex(g)
            print "\tv = %s" % convertToHex(v)
        if makeQuestion("Gostaria de digitar os pares de assinatura em vez de selecionar o arquivo?"):
            print "Insira o primeiro componente do par da assinatura r:"
            r = int(convertToDec(raw_input()))
            print "insira o segundo componente do par de assinatura s:"
            s = int(convertToDec(raw_input()))
        else:
            print "\nPor favor, insira o nome do arquivo"
            keysFile = raw_input()
            while not isThisFileExists(keysFile):
                print "\nArquivo inexistente!"
                print "Insira o nome correto do arquivo ou apert \"Ctrl + C\" para encerrar o programa"
                keysFile = raw_input()
            keys = getKeysFromFile(keysFile)
            assert(len(keys) == 2)
            r = keys[0]
            s = keys[1]
            print "\nPar de assinatura encontrado no arquivo:"
            print "\tr = %s" % convertToHex(r)
            print "\ts = %s" % convertToHex(s)
        print "\nIniciando validação de assinatura"
        if checkSignature(filename, (r,s), p, g, v):
            print "\nAssinatura válida!"
        else:
            print "\nAssinatura inválida!"
        
def encryptionAndSignatureFile(encryptionMethod, fileToEncrypt):
    something = 0

def decryptionAndSignatureCheck(encryptionMethod, fileToDecrypt):
    something = 0

def identifyEncryptionMethod(arg):
    if arg == "rsa" or arg == "elgamal":
        return arg
    else:
        return "desconhecido"

def identifyDigSignTask(arg):
    if arg == "check" or arg == "sign":
        if arg == "check":
            return "validação de assinatura"
        return "assinatura"
    else:
        return "desconhecida"

# ============================================== Menu =============================================  #

def menuBash():
    # Args são os argumentos passados na execução do programa
    args = list(sys.argv)
    args.remove(args[0])

    # Determina se o programa encerrou corretamente
    allDone = False

    # Contador do índice de argumento
    i = 0
    while not allDone:
    
        # Método de encriptação
        if args[i] == "--encrypt":
            i += 1
            encryptionMethod = identifyEncryptionMethod(args[i])
            print "==> Encriptação utilizando o método %s\n" % (encryptionMethod)
            if encryptionMethod == "desconhecido":
               break
            i += 1
            filenameToEncrypt = args[i]
            if isThisFileExists(filenameToEncrypt):
                print "Encripitando o arquivo %s" % (filenameToEncrypt)
                encryption(encryptionMethod, filenameToEncrypt)
                print "\nArquivo encriptado\n"
            else:
                print "Arquivo inexistente"
                break
            allDone = True

        # Método de decriptação
        elif args[i] == "--decrypt":
            i += 1
            decryptionMethod = identifyEncryptionMethod(args[i])
            print "==> Decriptação utilizando o método %s\n" % decryptionMethod
            if decryptionMethod == "desconhecido":
                break
            i += 1
            filenameToDecrypt = args[i]
            if isThisFileExists(filenameToDecrypt):
                print "Decripitando o arquivo %s\n" % (filenameToDecrypt)
                decryption(decryptionMethod, filenameToDecrypt)
                print "\nArquivo decriptado\n"
            else:
                print "Aquivo inexistente"
            allDone = True

        # --digsignature sign|check nameofFile
        elif args[i] == "--digsignature":
            i += 1
            method = args[i]
            print method
            task = identifyDigSignTask(args[i])
            if task == "desconhecida":
                break
            i+=1
            filename = args[i]
            if isThisFileExists(filename):
                print "==> Assinatura Digital\n"
                print "Realizando %s do arquivo %s" % (task, filename)
                signatureFile(filename, method)
            else:
                print "Aquivo inexistente"
                break
            allDone = True
    
        elif "--combinados":
            i += 1
            print "assinatura digital"
            break
    
        else:
            break
    if allDone ==  False:
        print "O programa será encerrado por falta de argumentos"

menuBash()
