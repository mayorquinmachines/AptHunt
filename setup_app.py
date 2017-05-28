def main():
    import subprocess
    import os
    install_lst = ['apache2', 'update', 'libapache2-mod-wsgi', 'python-flask', 'upgrade']
    print "Installing dependencies"
    for package in install_lst:
        cmd = 'sudo apt-get install '+ package
        subprocess.call(cmd.split(), shell=True)
    print "Moving directories and files"
    Flask_path = os.path.abspath('/AptHunt/FlaskApps/')
    os.rename(Flask_path, '/var/www/FlaskApps')
    os.rename('/var/www/FlaskApps/AptHunt.conf', '/etc/apache2/sites-available/AptHunt.conf')
    setup_cmd = [['a2enmod', 'wsgi'], ['apachectl', 'restart'], ['a2ensite', 'AptHunt'], ['service', 'apache2',
    'reload'], ['/etc/init.d/apache2/reload'], ['service', 'apache2', 'restart'], ['/etc/init.d/apache2/reload']]
    for cmd in install_lst:
        subprocess,call(['sudo']+cmd, shell=True)
    print "Done!"

if __name__ == "__main__":
  main()
