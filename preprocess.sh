cd ~/Users/edf/repos/prism_daily_weather/

# Create Final Output Directory
rm -rf ./scratch
mkdir ./scratch

# Loop Through Archives
for a in ./archive/*.zip
do
	# Unzip
    unzip $a -d ./scratch 
	
	# Loop Through Files in Archive
	for f in ./scratch/*.bil 
	do
		# Clip
		baseFilename=`basename -s .bil $f`
    	gdalwarp -overwrite -r bilinear -t_srs EPSG:4269 -ot Float32 -of GTiff -cutline ./mask/lac_mask.shp -crop_to_cutline ./scratch/${baseFilename}.bil ./scratch/${baseFilename}.tif
		
		# Clean
		rm ./scratch/${baseFilename}.bil
		rm ./scratch/${baseFilename}.bil.aux.xml
		rm ./scratch/${baseFilename}.hdr
		rm ./scratch/${baseFilename}.info.txt
		rm ./scratch/${baseFilename}.prj
		rm ./scratch/${baseFilename}.stx
	    
		# Convert and Collect Tmax
		TMAX="tmax"
		TMIN="tmin"
		TMEAN="tmean"
		
		if [[ $f =~ $TMAX ]]
		then
	    	raster2xyz ./scratch/${baseFilename}.tif ./scratch/${baseFilename}.csv
	    	STRING=${baseFilename:(-12)}
	    	DATE=${STRING:0:8}
	    	awk -F "," -v var=$DATE 'BEGIN { OFS = "," } FNR != 1 {$4=var; print}' ./scratch/$baseFilename.csv >> ./scratch/PRISM_tmax_stable_4kmM2_daily.csv
			
			# Clean
	    	rm -v ./scratch/${baseFilename}.csv
			rm -v ./scratch/${baseFilename}.tif
		
		# Convert and Collect Tmin
		elif [[ $f =~ $TMIN ]]
		then
		    raster2xyz ./scratch/${baseFilename}.tif ./scratch/${baseFilename}.csv
		    STRING=${baseFilename:(-12)}
		    DATE=${STRING:0:8}
		    awk -F "," -v var=$DATE 'BEGIN { OFS = "," } FNR != 1 {$4=var; print}' ./scratch/$baseFilename.csv >> ./scratch/PRISM_tmin_stable_4kmM2_daily.csv
			
			# Clean
		    rm -v ./scratch/${baseFilename}.csv
			rm -v ./scratch/${baseFilename}.tif
		
		# Convert and Collect Tmean
		elif [[ $f =~ $TMEAN ]]
		then 
		    raster2xyz ./scratch/${baseFilename}.tif ./scratch/${baseFilename}.csv
		    STRING=${baseFilename:(-12)}
		    DATE=${STRING:0:8}
		    awk -F "," -v var=$DATE 'BEGIN { OFS = "," } FNR != 1 {$4=var; print}' ./scratch/$baseFilename.csv >> ./scratch/PRISM_tmean_stable_4kmM2_daily.csv
			
			# Clean
		    rm -v ./scratch/${baseFilename}.csv
			rm -v ./scratch/${baseFilename}.tif
		fi
	done
done

# Add Headers
sed $'1s/^/x,y,tmax,dt\\\n&/' ./scratch/PRISM_tmax_stable_4kmM2_daily.csv > ./scratch/PRISM_tmax_stable_4kmM2_daily_final.csv
rm ./scratch/PRISM_tmax_stable_4kmM2_daily.csv

sed $'1s/^/x,y,tmin,dt\\\n&/' ./scratch/PRISM_tmin_stable_4kmM2_daily.csv > ./scratch/PRISM_tmin_stable_4kmM2_daily_final.csv
rm ./scratch/PRISM_tmin_stable_4kmM2_daily.csv

sed $'1s/^/x,y,tmean,dt\\\n&/' ./scratch/PRISM_tmean_stable_4kmM2_daily.csv > ./scratch/PRISM_tmean_stable_4kmM2_daily_final.csv
rm ./scratch/PRISM_tmean_stable_4kmM2_daily.csv

# Create Final Output Directory
rm -rf ./final
mkdir ./final

# Assemble
python ./py/assemble_outputs.py

# Clean
rm -rf ./scratch
