Esse é o código do TechChallenge do grupo 6. Desenvolvemos uma API para recuperar dados da Embrapa. 
Vamos explorar desde a captura de dados do site até a dockerização da aplicação.
Decidimos capturar os dados diretamente do site da embrapa, baixando arquivos CSV com as informações relevantes. 
Esses arquivos são salvos para que, caso o site fique offline, ainda seja possível acessar o último download realizado.
Para fazer o web scraping e coletar os dados do site, utilizamos a biblioteca BeautifulSoup. Em seguida, desenvolvemos a API usando FlaskAPI.
Implementamos a autenticação utilizando o método JWT (JSON Web Token). Como não podíamos usar um banco de dados, armazenamos as senhas hasheadas
em um .csv usando a biblioteca Bcrypt.
Para facilitar a implantação e garantir a portabilidade da nossa aplicação, dockerizamos a API utilizando o Docker.

A documentação foi feita utilizando Postman e está disponível no seguinte link:
https://documenter.getpostman.com/view/13216885/2sA3kdBxtz

A imagem do Docker está disponível no Docker Hub seguindo o seguinte link:
https://hub.docker.com/r/westerleycarvalho/tech_challenge

O vídeo de apresentação do trabalho está disponível no Youtube no seguinte link:
https://youtu.be/c2IhJyUSPcs
