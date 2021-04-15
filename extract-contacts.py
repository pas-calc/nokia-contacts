#!/usr/bin/env python

## Pascal ## 2021-02-09 18:16:01 -- 15/04/21

# importing required modules
from zipfile import ZipFile
import string
import vobject
import sys
import os
import base64
from datetime import datetime


# specifying the zip file name
file_name = "Backup001_20201008-contacts.NBF"

print "NOKIA CONTACT EXTRACTION"
print "------------------------"

if (len(sys.argv)==2):
	fn = sys.argv[1]
	print "using fn:",fn
else:
	print "no file given"
	sys.exit(1)


folder = "predefhiddenfolder/backup/WIP/32/contacts/"

# basename
def getbasename(path_to_file):
	return os.path.splitext(os.path.basename(path_to_file))[0]

# make ascii
def mkascii(s):
	printable = set(string.printable)
	return filter(lambda x: x in printable, s)

vcf_data = "";
with ZipFile(fn, 'r') as z:
    for filename in z.namelist():
		if filename.startswith(folder):
			data = z.read(filename)
			print(filename), len(data)
			vcf_data = vcf_data+data



print "."
# ~print vcf_data, len(vcf_data)
print "data length = ",len(vcf_data)
print "."

vcf_begin = "BEGIN:VCARD"
vcf_end   = "END:VCARD"

vcf_data = vcf_data.replace(vcf_begin, "\n\n"+vcf_begin).strip()
# ~vcf_data = vcf_data.decode('utf-8', 'ignore')

data_array = []
entries = []
fields = []


# use these fields (not photo)
usefields = ['N', 'ORG', 'TEL', 'FN', 'NOTE', 'X-NICKNAME', 'ADR', 'EMAIL', 'BDAY', 'URL']

for vcf_ in vcf_data.split(vcf_begin):
	if (vcf_.find(vcf_end) == -1):
		continue

	# ~vcf_ = mkascii(vcf_)

	vcf = vcf_[:vcf_.index(vcf_end)]
	vcf = vcf.replace(";ENCODING=8BIT","") # this encoding caused issues, like always.
	vcf = vcf.replace("\r\n ","") # dont break long lines
	vcf = vcf.strip()

	if (not "\nFN" in vcf): # add mandatory FN field
		vcf = vcf + "\n"+"FN:;;;;"

	entry = dict()

	for line in vcf.split("\n"):
		line = line.strip()
		parts = line.partition(':')

		field = parts[0].split(';')[0].strip()
		if ((not field in fields) and field):
			fields.append(field)

		if (not field in usefields):
			continue

		value = parts[-1].strip().split(';')
		text = ', '.join(filter(None, [v.replace("\t",'').strip() for v in value]))

		# ~print field,value
		# ~print "FIELD",field
		# ~print "VALUE",value

		if (not text):
			continue

		# special actions for these fields
		if (field=="NOTE"):
			text = base64.b64decode(value[0])
		if (field=="BDAY"):
			text = datetime.strptime(value[0][:8], "%Y%m%d").strftime("%Y-%m-%d")

		# ~print "TEXT", text

		# add field+value to entry
		if (field in entry):
			entry[field] = entry[field] + '; ' + text
		else:
			entry[field] = text

		# ~print ""

	# ~print entry

	dranda=True
	for e in entries:
		if (e['N'] == entry['N']): # check for duplicates (yes this happens)
			if (e == entry): # if the entries are completly identical no problem
				dranda=False # just dont add to the list
				continue
			print "ups problem with entry"
			print "old",e
			print "new",entry
			sys.exit(3)


	if dranda:
		entries.append(entry) # add entry to list

	data_array.append(vcf) # add fulltext vcf


	# ~print ""
	# ~print ""

######################

# make dir
outdir = getbasename(fn)+'_files'
print "create output directory: '"+outdir+"'"
os.mkdir(outdir)
os.chdir(outdir)
print "current dir:", os.getcwd()

# finished. print fields
print "fields found: ",fields

# ~print entries
entries.sort(key=lambda x: (''.join(reversed(x['N'].split(', ')))).lower())
# ~print entries

with open('entries.dict', 'w') as dictdump:
	dictdump.write(str(usefields)+"\n")
	dictdump.write("\n")
	for entry in entries:
		dictdump.write(str(entry)+"\n")

with open('export.csv', 'w') as csv_export:
	csv_export.write("# " + "\t".join(usefields) + "\n\n")
	for entry in entries:
		lin = []
		for field in usefields:
			if (field in entry):
				lin.append(entry[field])
			else:
				lin.append("NULL")
		csv_export.write("\t".join(lin) + "\n")


print "."
print "."

print "entries: ",len(entries)


# ~print vcf_data, len(vcf_data)
# ~print len(vcf_data)
# ~print len(data_array)

full_vcf = vcf_begin+"\n"+(("\n"+vcf_end+"\n\n"+vcf_begin+"\n").join(data_array))+"\n"+vcf_end
# ~print full_vcf
with open('alles.vcf', 'w') as the_file:
    the_file.write(full_vcf)






# ~-----------------------------------------------------------------------------------------------
sys.exit()

print "=========================================="

for v in data_array:
	vcf = vcf_begin+"\n"+v+"\n"+vcf_end
	print vcf
	# ~readComponents
	vcardlist = vobject.readComponents(vcf)
	# ~vcard = vobject.readOne(vcf)
	print type(vcardlist)
	print "..."
	for vcard in vcardlist:
		print type(vcard)
		print vcard
		print vcard.serialize()
		print vcard.prettyPrint

	# ~print vcard
	# ~vcard.prettyPrint()
	print "--------------------------------"

# ~vcard = vobject.readOne(full_vcf)
