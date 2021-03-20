import React, { useState, createRef, useEffect } from 'react'
import RGL, { WidthProvider } from 'react-grid-layout'

import { Tabs, Tab } from '@material-ui/core'
import ApexDataGrid from '../../../components/datagrid/ApexDataGrid'
import { TabPanel } from '../../../components/datagrid/TabPanel/TabPanel'

import { loadGridData, DATA_PATIENT_LIST, DATA_APEX_CLAIMS, DATA_APEX_BL_DOCS , DATA_APEX_EOB_DOCS} from './docuData'

const { ipcRenderer } = window.require('electron')
const ReactGridLayout = WidthProvider(RGL)

function App () {
  const [stateData, setstateData] = useState({
    dataPatientList: [],
    dataApexBLDocs: [],
    dataApexEOBDocs: [],
    dataApexClaims: [],
    filepath: '',
    iframeRef: createRef()
  })

  const [tablValue, settablValue] = useState(0);

  useEffect(() => {
    // loadGridData(DATA_APEX_CLAIMS, {}, recvGridData);
    // loadGridData(DATA_APEX_EOB_DOCS, {}, recvGridData);
    // loadGridData(DATA_APEX_BL_DOCS, {}, recvGridData);
  }, [])

  const handleGridRefresh = gridName => {
    switch (gridName) {
      case DATA_PATIENT_LIST:
        console.log('Refresh called on: ', gridName);
        //setstateData({ ...stateData, dataPatientList: [] })
        loadGridData(gridName, {}, recvGridData);
        break;

      case DATA_APEX_CLAIMS:
        console.log('Refresh called on: ', gridName);
        //setstateData({ ...stateData, dataApexClaims: [] })
        loadGridData(gridName, {}, recvGridData);
        break;

        case DATA_APEX_EOB_DOCS:
          console.log('Refresh called on: ', gridName);
          //setstateData({ ...stateData, dataApexEOBDocs: [] })
          loadGridData(gridName, {}, recvGridData);
          break;
          
          case DATA_APEX_BL_DOCS:
            console.log('Refresh called on: ', gridName);
            //setstateData({ ...stateData, dataApexBLDocs: [] })
            loadGridData(gridName, {}, recvGridData);
            break   ;       

      default:
    }
  }

  const recvGridData = (gridName, args, gridData) => {
    console.log('ReceivedData for :', gridName, args, gridData)

    switch (gridName) {
      case DATA_PATIENT_LIST:
        setstateData({ ...stateData, dataPatientList: gridData });
        break;
      case DATA_APEX_CLAIMS:
        setstateData({ ...stateData, dataApexClaims: gridData });
        break;
        case DATA_APEX_BL_DOCS:
          setstateData({ ...stateData, dataApexBLDocs: gridData });
          break;
          case DATA_APEX_EOB_DOCS:
            setstateData({ ...stateData, dataApexEOBDocs: gridData });
            break ;                 
      default:
    }
  }

  const onRowSelectExam = event => {
    let selectedNodes = event.api
      .getSelectedNodes()
      .filter(node => node.selected)
    console.log(selectedNodes)

    let datarow = selectedNodes[0].data
    console.log('Grid Row selected', datarow)

    // let filename = datarow.filename
    // let full_file_path = `\\\\192.168.1.17\\d$\\eClinicalWorks\\ftp\\apexdocs\\EOB\\${filename}`

    // full_file_path = full_file_path.replace('/', '\\')

    // console.log('Starting to get deposit ', full_file_path)

    // //let url = URL.createObjectURL(full_file_path);
    // const frame_element = `../public/pdfjs/web/viewer.html?file=${full_file_path}`

    // setstateData({ ...stateData, filepath: frame_element  })
  }

  const onRowSelectExamViewEcwDocument = event => {
    let selectedNodes = event.api
      .getSelectedNodes()
      .filter(node => node.selected)
    console.log(selectedNodes)

    let datarow = selectedNodes[0].data
    console.log('Grid Row selected', datarow)

    handleLinqReportPdf(data.dirpath + '/' + data.fileName);

  }


const handleLinqReportPdf = (filename) => {

  let full_file_path = `\\\\192.168.1.17\\d$\\eClinicalWorks\\ftp\\${filename}`;
  full_file_path = full_file_path.replace('/', '\\');

  console.log('Starting to get Linq File', full_file_path);

  const frame_element = `../public/pdfjs/web/viewer.html?file=${full_file_path}`;
  setstateData({ ...stateData, filepath: frame_element });

};


  const onRowSelectView = (datarow, gridname) => {
    console.log('Transaction View:', gridname, datarow)
    switch (gridname) {
      case DATA_APEX_CLAIMS:

      
    fetch(
        'https://192.168.21.199:8040/statement?patid=' +
          datarow.PatientId.toString()
      )
        //.then(this.handleErrors)
        .then((r) => r.blob())
        .then((blob) => {
          let url = URL.createObjectURL(blob);
          let viewerUrl = encodeURIComponent(url);
  
          const frame_element = `../public/pdfjs/web/viewer.html?file=${viewerUrl} `;
  
          setstateData({ ...stateData, filepath: frame_element });
        });

        break
        case DATA_APEX_BL_DOCS:
          case DATA_APEX_EOB_DOCS:

        handleLinqReportPdf(datarow.dirpath + '/' + datarow.filename);

        break;
      default:
    }
  }

  const handleTabChange = (event, newValue) => {
    //console.log("CHANGING TAB TO: " , newValue);
    //setPdfControl({ ...pdfControl, filepath: frame_element })
    settablValue(newValue)
  }

  const a11yProps = index => {
    //console.log("AllyProps", index);
    return {
      id: `simple-tab-${index}`,
      'aria-controls': `simple-tabpanel-${index}`
    }
  }

  return (
    <div className=' my-app container-fluid' style={{ position: 'relative' }}>
      <div className='row justify-content-start'>
        <div
          className='col-6 py-0 overflow-auto'
          style={{
            height: '100vh',
            width: '100%',
            backgroundColor: 'powderblue'
          }}
        >
          <Tabs
            value={tablValue}
            onChange={handleTabChange}
            aria-label='simple tabs example'
          >
            <Tab label='Claims' {...a11yProps(0)} />
            <Tab label='Billing Sheets' {...a11yProps(1)} />
            <Tab label='EOBs' {...a11yProps(2)} />
          </Tabs>
          <TabPanel
            value={tablValue}
            index={0}
          >
            <div className="container-fluid">
              <ReactGridLayout>
                <div
                  key='10'
                  data-grid={{ x: 0, y: 0, w: 14, h: 6, static: true, isResizable: false }}
                  style={{ height: '90%', width: '100%', margin: 0 }}
                >
                  <ApexDataGrid
                    key='claimlist'
                    gridname={DATA_APEX_CLAIMS}
                    ShowAllColumns={true}
                    gridTitle={''}
                    divHeight={'720px'}
                    onRefresh={() => handleGridRefresh(DATA_APEX_CLAIMS)}
                    gridData={stateData.dataApexClaims}
                    onRowSelected={onRowSelectExam}
                    button2Label='Stmt'
                    onButton2Callback={onRowSelectView}
                  />
                </div>
              </ReactGridLayout>
            </div>
          </TabPanel>
          <TabPanel value={tablValue} index={1}>
          <div className="container-fluid">
              <ReactGridLayout>
                <div
                  key='401'
                  data-grid={{ x: 0, y: 0, w: 14, h: 6, static: true, isResizable: false }}
                  style={{ height: '90%', width: '100%', margin: 0 }}
                >
                  <ApexDataGrid
                    key='bldocs'
                    gridname={DATA_APEX_BL_DOCS}
                    ShowAllColumns={true}
                    gridTitle={''}
                    divHeight={'720px'}
                    onRefresh={() => handleGridRefresh(DATA_APEX_BL_DOCS)}
                    gridData={stateData.dataApexBLDocs}
                    onRowSelected={onRowSelectExam}
                    button2Label='Stmt'
                    onButton2Callback={onRowSelectView}
                  />
                </div>
              </ReactGridLayout>
            </div>

          </TabPanel>
          <TabPanel value={tablValue} index={2}>
          <div className="container-fluid">
              <ReactGridLayout>
                <div
                  key='4012'
                  data-grid={{ x: 0, y: 0, w: 14, h: 6, static: true, isResizable: false }}
                  style={{ height: '90%', width: '100%', margin: 0 }}
                >
                  <ApexDataGrid
                    key='eobdocs'
                    gridname={DATA_APEX_EOB_DOCS}
                    ShowAllColumns={true}
                    gridTitle={''}
                    divHeight={'720px'}
                    onRefresh={() => handleGridRefresh(DATA_APEX_EOB_DOCS)}
                    gridData={stateData.dataApexEOBDocs}
                    onRowSelected={onRowSelectExam}
                    button2Label='Stmt'
                    onButton2Callback={onRowSelectView}
                  />
                </div>
              </ReactGridLayout>
            </div>
          </TabPanel>
        </div>
        <div
          className='col-6 py-0 overflow-auto'
          style={{
            height: '100vh',
            width: '100%',
            backgroundColor: 'powderblue'
          }}
        >
          <ReactGridLayout>
            <div
              key='21'
              data-grid={{ x: 0, y:0, w: 14, h: 6, static: true, isResizable: false }}
              style={{  width: '100%', margin: 0 }}
            >
              <iframe
                width='100%'
                height='820px'
                backgroundcolor='lightgrey'
                ref={stateData.iframeRef}
                src={stateData.filepath}
              />
            </div>
          </ReactGridLayout>
        </div>
      </div>
    </div>
  )
}

export default App
