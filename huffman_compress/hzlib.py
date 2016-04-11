import operator
'''
This module contains several function for compress and decompress data, using
the Huffman code algorithm.
'''

MAGIC = b"i2cshcfv1"
#Setting magic numbers for the length of a byte, a binary divisor and for eight
#bytes maximal decimal value
byte_length = 8
binary_divisor = 2
eight_byte = 256

def symbol_count(data):
    """
    This function gets as input data and return as output
    an dictionary which contains every character in data and number of times
    that every one of them shows in the data.
    """

    #Initilaizing a new dictionary
    symbol_count_dic = {}
    #A for loop running on data
    for char in data:    
        #If the char is already in the dictionary than add 1 to its counter, else
        #start it with 1 in the counter.
        symbol_count_dic[char] = symbol_count_dic.setdefault(char, 0) + 1
    return symbol_count_dic

def make_huffman_tree(counter):
    """
    This function gets as input counter which is the dictionary from the previous
    function that shows for every character the number it is in the string and
    return as output a binary tree which built in the model of huffman coding for
    the frequent which exists in counter.
    """
    #If the dictionary is empty return None
    if counter == {}:
        return None
    #Creating a new empty list
    nodes_list = []
    #Running a for loop in the length of counter - the given dictionary
    for key in counter:
        #Appending into nodes_list the key and the counter for that key
        nodes_list.append((key,counter[key]))
    #Sorting the list by the key
    nodes_list = sorted(nodes_list)
    #Sort the list by value and reverse it
    nodes_list = sorted(nodes_list,key = lambda tuples : tuples[1], reverse \
                        = True)
    #While theres two or more nodes
    while len(nodes_list) > 1:
        #Poping from the list the two last nodes the first is the one with the
        #smallest counter and the second is the second one
        first_node,second_node = nodes_list.pop(),nodes_list.pop()
        #Put in keys the keys of those two nodes
        keys = (second_node[0],first_node[0])
        #Summing the counters of both of them
        nodes_counter = second_node[1] + first_node[1]
        #Making a new tuple which is the parent containning the keys of the two
        #childs and theirs counters' sum.
        parent = (keys,nodes_counter)
        #Inserting this parent in the first place
        nodes_list.insert(0,parent)
        #Again sorting the list reversed by the value
        nodes_list = sorted(nodes_list,key = lambda tuples : tuples[1], reverse \
                            = True)
    return(nodes_list[0][0])

def build_codebook(huff_tree):
    """
    This function gets as input a binary tree that represent the huffman code and
    gives as output a dictionary which its key is the char and the value is a
    tuple contating the length of bytes needed to represent the number and a
    number which is the decimal value of the code
    """
    #Creating a new dictionary
    mapping_dic = {}
    #If the tree is empty
    if huff_tree == None:
        return mapping_dic
    #If the tree has only one node
    if isinstance(huff_tree,int):
        mapping_dic = {huff_tree : (1,0)}
        return mapping_dic

    def build_Huffman_code_table(huff_tree, prefix = ""):
        """
        builds a table of char: code pairs, given a code tree
        for demo only the code values are character sequences
        """
        #Creating a new dictionary
        table = {}
        #If the tree has only one node
        if isinstance(huff_tree,int):
            table[huff_tree] = prefix
        #Using the recurrence to find for every char its binary number in
        #the tree
        else:
            table.update(build_Huffman_code_table(huff_tree[1], prefix + '1'))
            table.update(build_Huffman_code_table(huff_tree[0], prefix + '0'))
        return table
    #A loop running in the length of the dictionary built in the
    #build_Huffman_code_table function based on huff_tree
    for index in build_Huffman_code_table(huff_tree):
        #Build the dictionary as requested when every char has his length -
        #means numbers of bytes being used to represent in binary show and the
        #binary presentation of that number 
        mapping_dic[index] = (len(build_Huffman_code_table(
            huff_tree)[index]), int(build_Huffman_code_table(
                huff_tree)[index],binary_divisor))
    return mapping_dic
        
        

def build_canonical_codebook(codebook):
    """
    This function gets as input the codebook which weve created in build_codebook
    and return as output a canonical_codebook table
    """
    #Creating a new dictionary which will be the returned codebook
    canonical_codebook = {}
    #Creating a new list
    new_list =[]
    #If the codebook is empty or contain only one element return as is
    if codebook == {} or len(codebook) == 1:
        return codebook
    #A for loop running in the range of codebook
    for index in codebook:
        #Put in new_list the keys and the lengths as tuples
        new_list.append((index,codebook[index][0]))
    #Sort the list by the key and the length
    new_list = sorted(new_list)
    new_list = sorted(new_list,key = lambda tuples : tuples[1])
    #Set the first element's "canonical huffman code" to be zero
    new_list[0] = (new_list[0][0],(new_list[0][1],0))
    #Save in code the first value from the tuple
    code = new_list[0][1][0] 
    #A for loop running from the second element till the end of new_list
    for i in range(1,len(new_list)):
        #If the length is bigger than the code we saved from the previous element
        if new_list[i][1] > code:
            #save in power 2 power the difference between the current length and
            #code
            power = 2**(new_list[i][1] - code)
            #Put in new_list in the current place the current key and current
            #length and taking the code from previous element + 1 and multiply
            #in power
            new_list[i] = (new_list[i][0],(new_list[i][1],(new_list[i-1][1][
                1] + 1) * power))
            #Changing code to be the current code
            code = new_list[i][1][0] 
        #If the length is not bigger than the code
        else:
            #Put in new_list in the current place the current key, current
            #length and the previous code + 1
            new_list[i] = (new_list[i][0],(new_list[i][1],(new_list[i-1][
                1][1] + 1)))
    #A for loop running in the length of new_list
    for j in range(len(new_list)):
        #Put in the dictionary the matchs values for the keys. 
        canonical_codebook[new_list[j][0]] = new_list[j][1]
    return canonical_codebook
        

def build_decodebook(codebook):
    """
    This function gets as input the codebook which weve created in build_codebook
    and returns as output a dictionary which maps bytes sequence to the matchs
    chars
    """
    #Change the key with the value
    codebook = {value:key for key,value in codebook.items()}
    return codebook

def compress(corpus, codebook):
    """
    This function gets as input the codebook which weve created in build_codebook
    and a corpus and yields as output 0 or 1 as the value of the binary
    presentation. 
    """
    #A for loop running on corpus
    for char in corpus:
        #Taking the number from current char
        current_num = (codebook[char][1])
        #Show the num in a binary presentation
        current_num = bin(current_num)[2:]
        #If the len of the num in binary presentation is shorter than the len it
        #should be
        if len(current_num) < codebook[char][0]:
            #Add to the num zeros in the beginning so it'll be in the required
            #length
            current_num = ("0" * (codebook[char][0] - len(current_num)) +\
                           current_num)
        #A for loop running in the length of the num
        for i in range(len(current_num)):
            #yielding the current number of it - 0 or 1
            yield int(current_num[i])
        
            
        
def decompress(bits, decodebook):
    """
    This function gets as input the decodebook and a sequence of bits and yields
    as output the match value for the bite/s
    """
    #Creating a new empty string
    sequence = ""
    #A loop running on bits
    for bit in bits:
        #Add to sequence the current bit and change it to string
        sequence += str(bit)
        #Creating a tupple contains the length of the sequence and the decimal
        #presentation of the number
        tup = (len(sequence),int(sequence,binary_divisor))
        #If this tupple is in the decodebook
        if tup in decodebook:
            #Yield it's value
            yield decodebook[tup]
            #Re-init the sequence
            sequence = ""
    

def pad(bits):          
    """
    This function gets as input a sequence of bits and yields as output the value
    of byte an integer between 0 and 255
    """
    #Creating a new empty string
    sequence = ""
    #A loop running on bits
    for bit in bits:
        #Adding to sequence the current bit
        sequence += str(bit)
        #If the length of the sequence is 8 yield its decimal value and init the
        #sequence
        if len(sequence) == byte_length:
            yield int(sequence, binary_divisor)
            sequence = ""
    #Add 1 to the end of the sequence and a sequence of 0's as needed in order
    #to make the length of the sequence to 8.
    sequence += "1"
    sequence += (byte_length-len(sequence)) * "0"
    yield int(sequence, binary_divisor)
        
def unpad(byteseq):
    """
    This function gets as input a byte's sequence and is the reversed action
    of pad, means remove the 1 and zeros in the end and yields 1 or 0.
    """
    #Creating a new list
    digit_seq = []
    #A loop running on the given byte sequence
    for byte in byteseq:
        #Taking the binary presentation of the current byte
        binary_number = bin(byte)[2:]
        #While the len of the number is shorter than 8
        while len(binary_number) < byte_length:
            #Adding zero to the beginning of the number
            binary_number = "0" + binary_number
        #A for loop running on the binary number
        for digit in binary_number:
            #Appending the digit to the sequence
            digit_seq.append(int(digit))
    #If the last digit is 0 I pop it out of the sequence
    while digit_seq[-1] == 0:
        digit_seq.pop()
    #Now i remove the 1 that I added when i was doing pad
    digit_seq = digit_seq[:-1]
    for item in digit_seq:
        yield item


def join(data, codebook):
    """
    This function gets as input a codebook which is a canonical table and data
    which is a sequence value of bytes and yields as output first the
    presentation of codebook as sequence of bytes and than the values from data.
    """
    #Creating a new list
    joined_info = []
    #A for loop running 256 times
    for num in range(eight_byte):
        #Adding 0 to the list
        joined_info.append(0)
    #A for loop running on codebook
    for key in codebook:
        #Adding the value on key's first place in codebook to the list
        joined_info[key] = codebook[key][0]
    #A foor loop running on data
    for index in data:
        #Adding to the end of the list the indexes of the data
        joined_info.append(index)
    for char in joined_info:
        yield char

def split(byteseq):
    """
    This function gets as input byteseq, split it to data and codebook and
    yields as output a tuple which its first value is a canonic table
    represented by 256 first bytes in bytseq and the second value is an iterator
    which pass on byteseq as value of bytes
    """
    #Creating a new list and dictionary
    codes_list = []
    coding_dic = {}
    #Changing byteseq to be a list
    byteseq = list(byteseq)
    #Splitting the input to data the part from place 256 till the end
    data = byteseq[eight_byte:]
    data = (char for char in data)
    #Taking the first part from the input from beginning till place 256
    codes_list = byteseq[:eight_byte]
    #A for loop running in the length of codes_list
    for value in range(len(codes_list)):
        if codes_list[value] != 0:
            coding_dic[value] = (codes_list[value],0)
    #Taking the dictionary and using build_canonical_codebook to create a
    #canonical codebook from it
    return data,build_canonical_codebook(coding_dic)

    
