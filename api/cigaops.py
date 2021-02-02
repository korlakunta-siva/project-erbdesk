import paramiko
import os
import argparse
import datetime
import glob
import pandas as pd
import json
import re
import sys
from elasticsearch import Elasticsearch
from elasticsearch.client import SqlClient
import urllib3


def sudo_run_commands_remote(command, server_address, server_username, server_pass, server_key_file):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=server_address,
                username=server_username,
                password=server_pass,
                key_filename=server_key_file)
    session = ssh.get_transport().open_session()
    session.set_combine_stderr(True)
    session.get_pty()
    session.exec_command("sudo bash -c \"" + command + "\"")
    stdin = session.makefile('wb', -1)
    stdout = session.makefile('rb', -1)
    stdin.write(server_pass + '\n')
    stdin.flush()
    print(stdout.read().decode("utf-8"))


def run_unix_process(campus, unixprocess = None):

    unix_hostname = 'iasq1mr2'
    if campus == 'R' :
           unix_hostname = 'iasq1mr2'   #iasp1fo1
    if campus == 'S' :
           unix_hostname = 'iasp1ma1'
    if campus == 'J' :
           unix_hostname = 'iasp1mf2'

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    cmd = 'sudo -u ciguser ps -Ao "%p,%P,%u,%U,%c,%x,%t,%a"'
    # cmd = 'sudo -u ciguser /cigaapp/ciguser/bin/scripts/stop_processors.sh'
    # cmd = 'sudo -u ciguser cd /cigaapp/ciguser/bin/scripts; /cigaapp/ciguser/bin/scripts/batch_start_processor.sh'
    # cmd = 'sudo -u ciguser  /cigaapp/ciguser/bin/scripts/start_processor.pl 3 2'
    # cmd = 'sudo -u ciguser  kill -9 29163632'


    unixprocess = cmd
    ssh.connect(unix_hostname, username="mra9895", password="MyPass")
    # stdin, stdout, stderr = ssh.exec_command(
    #     "sudo su - ciguser")

    stdin, stdout, stderr = ssh.exec_command(unixprocess)
    stdin.flush()
    sql_text=""
    rowcounter=0

    data = stdout.read().splitlines()
    #print("output", data)
    #for i, line in enumerate(stdout):
    #    line = line.rstrip()
    ssh.close()
    return (data)


def unix_ps(request) :
    html_table = ""
    for campus in ['R', 'J', 'S' ] :
        try :
            ps_data = run_unix_process(campus)
            #TESTDATA = StringIO(ps_data)
            #df = pd.read_csv(TESTDATA, sep=",")
            ps_output = []
            ps_receivers = []
            ps_processors = []
            head_rowline = ps_data[0].decode('ascii')
            head_rowline = re.sub(' +', ' ', head_rowline)
            head_rowline = re.sub('^ *', '', head_rowline)
            head_rowline = re.sub(' ', ',', head_rowline)

                #rowline = re.sub(' +', ' ', rowline)
            column_names = [col for col in head_rowline.split(',') ] # Get column names from output
            column_names[-1] = "CommandArgs"


            for line in ps_data[1:] :
                #print ("Received {0}", line.decode('ascii'))
                rowdict = {}
                rowline = line.decode('ascii')
                row = rowline.split(',')
                rowdict.update({name: row[i] for i, name in enumerate(column_names)})
                if rowdict['USER'].strip(' ') == 'ciguser' :
                    ps_output.append(rowdict)
                if 'CIGDicomReceiver' in rowdict['CommandArgs'].strip(' ') :
                    ps_receivers.append(rowdict)
                if 'CIGProcessor' in rowdict['CommandArgs'].strip(' ') :
                    ps_processors.append(rowdict)

            html_table = html_table + "<h2 align='center'>CIG Processes in Campus: " + campus + " at: " + datetime.now().strftime("%m-%d-%Y %H:%M") + " </h2>"
            #df = pd.read_sql(dbspace_sql,cnxn)
            pd.set_option('display.max_columns', None)
            pd.set_option('display.max_colwidth', -1)
            df = pd.DataFrame(ps_output)  #.sort_values(['server', 'database', 'table'], ascending=[1, 1, 1])
            df_receivers = pd.DataFrame(ps_receivers)
            df_processors = pd.DataFrame(ps_processors)

            html_table = html_table + "<h3 align='center'>Receivers : " + str(len(ps_receivers)) + "</h3>" + df_receivers.to_html()
            html_table = html_table + "<h3 align='center'>Processors : " + str(len(ps_processors)) + "</h3>" + df_processors.to_html()
            #print(html_table)

            #html_table = html_table + df.to_html(index=False) #,  columns = ['s_table', 's_daystokeep', 'd_table', 'd_daystokeep', 's_host', 's_db',  'd_host', 'd_db'  ])

            #print(ps_output)
        except Exception as e:
            print (e)
            pass

    template_string = """
            {% extends "prefetch/layout.html" %}
            {% block content %}
            <div>
      """

    template_string = template_string + '''

            {% if graph %}
                <div >
                {{ graph|safe }}
                </div>
            {% endif %}
            {% if html_graph %}
                <div >
                {{ html_graph|safe }}
                </div>
            {% endif %}

      '''

    template_string = template_string + '''
            </div>
            {% endblock %}
        '''
    template_string = template_string + '''
        {% block scripts %}

<script>
    $(function () {

    function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
            // Only send the token to relative URLs i.e. locally.
            //xhr.setRequestHeader("X-CSRFToken", getCookie('csrfmiddlewaretoken'));
            //alert('Setting csrftoken:' + getCookie('csrfmiddlewaretoken'))
        }
    }
});


        $(".dtpick").datepicker("option", "altFormat", "yy-mm-dd");
        $(".dtpick").datepicker({
                        onSelect: function(dateText, inst) {
                                    var dateAsString = dateText; //the first parameter of this function
                                    var dateAsObject = $(this).datepicker( 'getDate' ); //the getDate method
                                    window.location.href = '/ciga_queue_manager?repdate=' + dateAsString;
                                    return false;
                        }
        });

 });

</script>

            {% endblock %}
        '''

            #'controlform' : choicesForm,
            #'html_graph' : html_table
    output1 = render_dynamic_djangoview(request, template_string, 'dynamic_view',
        {
            'title':'Dashboard',
            'message':'CIS Dashboard page.',
            'year':datetime.now().year,
            'html_graph' : html_table

        })

    return output1

def live_ciga_scan_df(campus):

    unix_hostname = 'iasp1fo1'
    if campus == 'R' :
           unix_hostname = 'iasp1fo1'
    if campus == 'S' :
           unix_hostname = 'iasp1ma1'
    if campus == 'J' :
           unix_hostname = 'iasp1mf2'
    if campus == 'A' :
           unix_hostname = 'iasq1mr2'

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh.connect(unix_hostname, username="mra9895", password="MyPass")
    # stdin, stdout, stderr = ssh.exec_command(
    #     "sudo su - ciguser")
    stdin, stdout, stderr = ssh.exec_command(
        "sudo -u ciguser df -g")

    stdin.flush()
    sql_text=""
    rowcounter=0

    data = stdout.read().splitlines()
    #print(data)
    currentdate = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%m-%d-%Y 10:10:10")

    sharedata = []
    try:
        for line in data:
            #print ("Received {0}", line.decode('ascii'))
            rowline = line.decode('ascii')

            if (rowline.lower().startswith('filesystem')):
                continue
            if (currentdate==None):
                continue
            rowline = re.sub(' +', ' ', rowline)
            rowline = re.sub(' ', '|', rowline)
            #print ("%s => %s \n", currentdate, rowline)
            rowline = currentdate +'|' + rowline
            rowline = rowline.strip('\n')
            rowline = rowline.replace('%', '')
            row = rowline.split('|')
            shareinfo = {
              'date' : row[0],
              'campus': campus,
              'gb_blocks': row[1],
              'gb_blocks_free': row[2],
              'gb_pct_used' : row[3],
              'mounted_on' : row[7]
            }

            #print(shareinfo)

            sharedata.append(shareinfo)
            # if  1 == 1 :
            #     rowcounter += 1
            #     sql_text =  ("if not exists (select 'x' from cis_store_usage where csu_date = '" + row[0] + "' and csu_campus = '" + campus + "' and csu_store_name = '" + row[1] + "') "
            # "INSERT INTO cis_store_usage "
            #     "(csu_date,csu_campus, csu_store_name,gb_blocks,gb_blocks_free,gb_blocks_pct_used,Inodes_used,Inodes_pct_used,csu_mounted_on) "
            # "VALUES ('" + row[0] + "', '" + campus  + "', '" + row[1] + "' , " + str(row[2]) + ", " + str(row[3]) + ", " + str(row[4]) + ", " + str(row[5]) + ", " + str(row[6])  + ", '" + row[7] + "') " )
            #     try:
    except:
        pass

    ssh.close()
    print (sharedata)

def main():

  parser = argparse.ArgumentParser(description="Python Local OS Commands Runner")
  group = parser.add_mutually_exclusive_group()
  group.add_argument("-v", "--verbose", action="store_true")
  group.add_argument("-q", "--quiet", action="store_true")
  parser.add_argument("-host", "--host",  help="hostname", default=None)
  parser.add_argument("-cmd",  help="command_to_run")
  parser.add_argument("-p", "--pid", type=int, help="pid", default=None)
  args = parser.parse_args()

  command = None
  hostname = None
  pid = None

  if args.cmd :
    command = args.cmd
  if args.host :
    hostname = args.host
  if args.pid :
      pid = args.pid


  html_table = ""
  campus = 'R'

  if command.strip() == 'testdb' :
    print("Started test DB")
    urllib3.disable_warnings()
    http = urllib3.HTTPSConnectionPool('iasq1mr2', port=8081, cert_reqs='CERT_NONE', assert_hostname=False)

#     pat_exams_sql = '''set rowcount 0 select exam_id from EXAM exm where patient_id = {0}
# and exm.performed_dt < dateadd(mm, -8, getdate())
# and exists ( select 'x' from img_study, img_series, img_series_location, img_store
# where exam_id =  exm.exam_id and imgser_imgsty_id = imgsty_id and imgserl_imgser_id = imgser_id
# and imgserl_imgstr_id = imgstr_id and imgstr_imgsys_id = 2 and  imgserl_status = 'A') '''.format(patid)


    pat_exams_sql = ''' select @@servername as servername , db_name() as dbname , suser_name() as login '''

    rows = []
    try :
        urlstring="https://iasq1mr2:8081/exsql?dbserver=iimsProd&sqltype=patientsToPurge&param1=5"
        urlstring="https://iasq1mr2:8081/exsql?dbserver=iimsRepl&sqltype=customSQL&sqltext=" + pat_exams_sql
        r = http.request('GET', urlstring)
        r.release_conn()
        data_frame = json.loads(r.data.decode('utf-8'))
        rows  = json.loads(data_frame['frame0'])['rows']
        print("Purging:" , rows)
        return rows
    except Exception as ex:
        print ('Error Calling URL for patientToPurgetid. Error:  %s ' %  ( ex ))
    finally:
        pass

    print(rows)
    sys.exit(0)

  if command.strip() == 'testes' :
    print("Started testes")
    es =  Elasticsearch(
              [
                  'https://slk02:MyPass@bigdata.mayo.edu/es/7x/PROD3'
              ],
              verify_certs=True
          )

    #  TEST   'https://slk02:MyPass@test.bigdata.mayo.edu/es/7x/TEST3'

    # json_data = json.dumps({"query": "DESCRIBE \"as-log-metrics-2019.06.14\" "})
    # r = requests.post("http://localhost:9200/_sql?format=csv", data=json_data, headers={'Content-Type':'application/json'})
    # print(r.text)

    json_query_data = json.dumps({"query": "SELECT patient_cmrn, count(*) FROM \"imsu-dashboardusers___cis_storage*\" group by patient_cmrn limit 1000 "})
    json_query_data = json.dumps({"query": "SELECT image_store_name, sum(image_count) FROM \"imsu-dashboardusers___cis_storage*\" group by image_store_name limit 100 "})
    json_query_data = json.dumps({"query": "SELECT * FROM \"imsu-dashboardusers___cis_storage*\" order by patient_cmrn limit 100 "})
    # r = requests.post("http://localhost:9200/_sql?format=csv", data=json_data, headers={'Content-Type':'application/json'})
    # print(r.text)


    #res = es.sql.query(body = '{ "query": "SELECT \* FROM \"imsu-dashboardusers___cis_storage*\"  DESC LIMIT 5" }', format = 'json')
    res = es.sql.query(body = json_query_data , format = 'json')

    # res = es.search(index="imsu-dashboardusers___cis_storage*", body={"query": {"match_all": {}}})
    # client.SqlClient.query
    print(res)
    # print("Got %d Hits:" % res['hits']['total']['value'])
    # for hit in res['hits']['hits']:
    #     print(hit["_source"])

    sys.exit(0)


  if command.strip() == 'testdf' :
    print("Started testdf")
    live_ciga_scan_df('A')
    sys.exit(0)

  if command.strip() == 'testps' :
    print("Started testps")
    try :
                ps_data = run_unix_process('R')
                #print(ps_data)
                #TESTDATA = StringIO(ps_data)
                #df = pd.read_csv(TESTDATA, sep=",")
                ps_output = []
                ps_receivers = []
                ps_processors = []
                head_rowline = ps_data[0].decode('ascii')
                head_rowline = re.sub(' +', ' ', head_rowline)
                head_rowline = re.sub('^ *', '', head_rowline)
                head_rowline = re.sub(' ', ',', head_rowline)

                    #rowline = re.sub(' +', ' ', rowline)
                column_names = [col for col in head_rowline.split(',') ] # Get column names from output
                column_names[-1] = "CommandArgs"


                for line in ps_data[1:] :
                    #print ("Received {0}", line.decode('ascii'))
                    rowdict = {}
                    rowline = line.decode('ascii')
                    row = rowline.split(',')
                    rowdict.update({name: row[i] for i, name in enumerate(column_names)})
                    if rowdict['USER'].strip(' ') == 'ciguser' :
                        ps_output.append(rowdict)
                    if 'CIGDicomReceiver' in rowdict['CommandArgs'].strip(' ') :
                        ps_receivers.append(rowdict)
                    if 'CIGProcessor' in rowdict['CommandArgs'].strip(' ') :
                        ps_processors.append(rowdict)

                html_table = html_table + "<h2 align='center'>CIG Processes in Campus: " + campus + " at: " + datetime.datetime.now().strftime("%m-%d-%Y %H:%M") + " </h2>"
                #df = pd.read_sql(dbspace_sql,cnxn)
                pd.set_option('display.max_columns', None)
                pd.set_option('display.max_colwidth', None)
                df = pd.DataFrame(ps_output)  #.sort_values(['server', 'database', 'table'], ascending=[1, 1, 1])
                df_receivers = pd.DataFrame(ps_receivers)
                df_processors = pd.DataFrame(ps_processors)

                html_table = html_table + "<h3 align='center'>Receivers : " + str(len(ps_receivers)) + "</h3>" + df_receivers.to_html()
                html_table = html_table + "<h3 align='center'>Processors : " + str(len(ps_processors)) + "</h3>" + df_processors.to_html()
                host_ps = {
                  'campus': campus,
                  'receivers': ps_receivers,
                  'processors' : ps_processors
                }
                print(host_ps)

                #html_table = html_table + df.to_html(index=False) #,  columns = ['s_table', 's_daystokeep', 'd_table', 'd_daystokeep', 's_host', 's_db',  'd_host', 'd_db'  ])

                #print(ps_output)
    except Exception as e:
                print (e)
                pass

if __name__ == "__main__":
    main()
