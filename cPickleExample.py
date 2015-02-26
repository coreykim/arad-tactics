import cPickle

a = range(5)

file_Name = "testsavefile"
fileObject = open(file_Name, 'wb')
cPickle.dump(a, fileObject)
fileObject.close()

fileObject = open(file_Name, 'r')
b = cPickle.load(fileObject)

print b