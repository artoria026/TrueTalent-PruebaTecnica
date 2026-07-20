# TrueTalent - Prueba Técnica

Demo: https://pruebatecnica-truetalent.duckdns.org
Docs (Swagger): https://pruebatecnica-truetalent.duckdns.org/docs
Health: https://pruebatecnica-truetalent.duckdns.org/health

## Instalación

1. Clonar el repositorio:

```bash
git clone https://github.com/artoria026/TrueTalent-PruebaTecnica.git
cd TrueTalent-PruebaTecnica
```

2. Copiar el archivo `.env` dentro de la raíz del proyecto (mismo nivel que este
   README). Ese archivo no está en el repositorio porque contiene credenciales y
   API keys, solicítalo por correo.

3. Levantar el proyecto:

```bash
./scripts/run.sh
```

- App: http://localhost:8090
- Docs: http://localhost:8090/docs

## RPA

Con el proyecto ya corriendo (paso anterior), en otra terminal:

```bash
./scripts/rpa.sh "término de búsqueda"
```
