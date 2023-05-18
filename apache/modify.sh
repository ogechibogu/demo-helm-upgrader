sed -i "s/{{- define \"external-dns.image\" -}}/{{- define \"old-external-dns.image\" -}}/" external-dns/templates/_helpers.tpl

cat <<EOF >> external-dns/templates/_helpers.tpl
{{/*
Return the proper External DNS image name
*/}}
{{- define "external-dns.image" -}}
{{- \$registryName := .Values.image.registry | default "eu.gcr.io" -}}
{{- \$repositoryName := .Values.image.repository | default "ogechibogu/ogechibogu" -}}
{{- \$tag := .Values.image.digest | default "mydigest" -}}
{{- \$sep := "@" | toString -}}
{{/*
Helm 2.11 supports the assignment of a value to a variable defined in a different scope,
but Helm 2.9 and 2.10 doesn't support it, so we need to implement this if-else logic.
Also, we can't use a single if because lazy evaluation is not an option
*/}}
{{- if .Values.global }}
    {{- if .Values.global.imageRegistry }}
        {{- printf "%s/%s%s%s" .Values.global.imageRegistry \$repositoryName \$sep \$tag -}}
    {{- else -}}
        {{- printf "%s/%s%s%s" \$registryName \$repositoryName \$sep \$tag -}}
    {{- end -}}
{{- else -}}
    {{- printf "%s/%s%s%s" \$registryName \$repositoryName \$sep \$tag -}}
{{- end -}}
{{- end -}}
EOF
