cd data
END=200

# Convert documents to pdf using Libreoffice
docs=$(find "documents/" -type f -iname "*.docx")
for i in $docs; do
    [ -f "$i" ] 
    echo Convert "$i" to pdf 
    /usr/bin/libreoffice --headless --convert-to pdf "$i" --outdir pdf/
done

# After conversion of word document start extracting text
pdfs=$(find "pdf/" -type f -iname "*.pdf")
for i in $pdfs; do
    [ -f "$i" ]     
    echo Extract text per page for "$i"
    filename=$(basename -- "$i")
    extension="${filename##*.}"
    filename="${filename%.*}" 
    for j in $(seq 1 $END); 
        do pdftotext -f $j -l $j -layout "$i" "./text/${filename}_${j}" || break; done
done

