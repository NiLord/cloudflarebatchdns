# Script para actualizar registro A con la dirección publica del host

## Como builder la imagen

```shell
docker build -t cloudflarebatch:1.0 --build-arg CLOUDFLARE_EMAIL='{TU_EMAIL}' --build-arg CLOUDFLARE_API_KEY='{CLOUDFLARE_KEY}' --build-arg CLOUDFLARE_DOMAINS='{TU_DOMINIOS_SEPARADOS_POR_COMAS}' .
```

**Pendientes:**
* Pasar el API key a un secret y no usarlo como env del contenedor al tener data sensible.