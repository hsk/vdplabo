find . -type f -not -path '*/.*' -print0 | xargs -0 md5 | awk '{print $4}' | sort | uniq -d | xargs -I {} grep "{}" <(find . -type f -not -path '*/.*' -print0 | xargs -0 md5) 
