## Currency Exchange
### Gitlab CI with Heroku
- Create repo on Gitlab
- Create Account on Heroku and get API Key
- Create Two different app, one for staging and one for production

> Note: We need to add enviroment variables in Gitlab, HEROKU_API, HEROKU_STAGING_APP, HEROKU_PRODUCTION_APP

- create .gitlab-ci.yml file in root dirctory of project
- Before any of the things we need to install python, pip and dpl(deployment tool), so we will add this in before_script

```sh
before_script:
    - sudo apt install python3.8
	- sudo apt install python3-pip
	- gem install dpl
```

- now we need to define the stages
```sh
stages:
	- staging
	- production
```
- Next we need to tell ci what needs to be done in each stage
```sh
staging:
	type: deploy
	stage: deploy
	image: docker-image-name
	script:
        - dpl --provider=heroku --app=$HEROKU_STAGING_APP --api-key=$HEROKU_API
    only:
        - staging

production:
    type: deploy
    stage: production
    image: docker-image-name
    script:
        - dpl --provider=heroku --app=$HEROKU_PRODUCTION_APP --api-key=$HEROKU_API
    only:
        - master
```

Now whenever you push something to staging or master branch this CI will automatcally start deploying to Heroku
