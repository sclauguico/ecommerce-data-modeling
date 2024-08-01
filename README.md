## eCommerce Data Modeling 

A data modeling project utilizing PostgreSQL and pgAdmin, running on Docker containers.

### Add a Docker Compose Setup with PostgreSQL and pgAdmin4


#### Steps:

1. Create a docker-compose.yml file under the root directory
ecommerce-data-modeling > docker-compose.yml
  ```yml
  version: "3.8"
  services:
    db:
      container_name: postgres_container
      image: postgres
      restart: always
      environment:
        POSTGRES_USER: root
        POSTGRES_PASSWORD: root
        POSTGRES_DB: test_db
      ports:
        - "5432:5432"
    pgadmin:
      container_name: pgadmin4_container
      image: dpage/pgadmin4
      restart: always
      environment:
        PGADMIN_DEFAULT_EMAIL: admin@admin.com
        PGADMIN_DEFAULT_PASSWORD: root
      ports:
        - "5050:80"
  ```

2. Install [Docker Desktop](https://docs.docker.com/desktop/install/windows-install/), and follow installation procedure from the deocumentation.

3. Open Docker Desktop

4. On the terminal, run:
  ```
  docker pull postgres
  docker-compose up
  ```

5. On your browser of choice, enter localhost:5050. You will the the pgAdmin UI

6. Enter the credentials set on the docker-compose.yml
  ```
  email: admin@admin.com
  password: root
  ```

7. Click login

8. Open a new terminal and run
  ```
  docker container ls
  ```

9. Copy postgres container ID and run
  ```
  docker inspect <container-id>
  ```

10. Copy the IPAddress. For example: 172.18.0.2

11. On pgAdmin, click Add New Server

12. Add name. For example: ps_db

13. Go to connection tab and 
  a. Add the IPAdress. For example: 172.18.0.2
  b. Set username to root
  c. Enter the password: root
  d. Save

14. Under servers, you'll see postgres and test_db databases
  Note: test_db is the database set up in the .yml file