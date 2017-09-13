let scene = document.querySelector('a-scene');
let sky = document.querySelector('a-sky');
let objectContainer = document.querySelector('#object-container');

let eegData = [];

var oscPort = new osc.WebSocketPort({
  url: "ws://192.168.129.160:8081", // URL to your Web Socket server.
  metadata: true
});

oscPort.open();

oscPort.on("message", function (oscMsg) {
  //console.log(oscMsg);
  if(oscMsg.address == '/muse/elements/theta_delta') {
    //console.log(oscMsg);

    eegData.push(oscMsg.args.map(v => v.value));
  }
});

// random num generator
function getRandomNumber(x, y) {
  return Math.floor(Math.random() * x + y);
}

// get random hex color
function getRandomColor() {
  let letters = '0123456789abcdef';
  let randomColor = '';
  for (let i = 0; i < 6; i++) {
    randomColor += letters[Math.floor(Math.random() * 16)];
  }
  return randomColor;
}

function getRingColor(ring_index) {
  let color = 'ffffff';
  switch(ring_index) {
    case 0:
      color = 'ff0000';
      break;
    case 1:
      color = 'ff00ff';
      break;
    case 2:
      color = '00ff00';
      break;
    case 3:
      color = '00ffff';
      break;
    case 4:
      color = '0000ff';
      break;
  }
  return color;
}

function getPreviousOscValue(index) {
  let value = 10 + index;
  if(eegData.length > 0) {
    //console.log(Math.max(...eegData.map(d => d[index])));
  }
  return value;
}
function getOscValue(index) {
  let value = -10 + index;
  if(eegData.length > 0) {
    //console.log(Math.min(...eegData.map(d => d[index])));
  }
  return value;
}

// set sky values
sky.setAttribute('color', `#${getRandomColor()}`);
sky.setAttribute('animation__color', `property: color; dir: alternate; dur: 2000; easing: easeInOutSine; loop: true; to: #${getRandomColor()}`);

// change this value for more or less rings
let totalRingElements = 5;

let currentHeight = 0;
function checkHeight() {
  //console.log('check');
  //console.log(eegData);
  var camera = document.querySelector('#camera');
  currentHeight += 0.1;
  camera.setAttribute('position', '0 ' + currentHeight + ' 0');
  eegData = [];
}

function generateAllElements() {
  //console.log('generate');
  while (objectContainer.firstChild) {
    objectContainer.removeChild(objectContainer.firstChild);
  }

  let maxValues = [];
  let minValues = [];
  for(let a = 0; a < totalRingElements; a++){
    maxValues.push(10);
    minValues.push(-10);
  }

  if(eegData.length > 0) {
    for(let a = 0; a < totalRingElements; a++){
      maxValues[a] = Math.max(...eegData.map(d => d[a]));
      minValues[a] = Math.min(...eegData.map(d => d[a]));
    }

    for(let a = 0; a < totalRingElements; a++){
      const maxValue = Math.max(...maxValues);
      const minValue = Math.min(...minValues);

      maxValues = maxValues.map(v => Math.ceil(v / 100));
      minValues = minValues.map(v => -10 + Math.ceil(v / 100));
    }
  }

  for(let a = 0; a < totalRingElements; a++){

    // element params
    //let totalCircleElements = getRandomNumber(10, 3);
    //let elementScale = getRandomNumber(3, 1);
    //let scaleDuration = getRandomNumber(3000, 1000);
    let totalCircleElements = 8;
    let elementScale = 1;
    let scaleDuration = 5000;

    // path params
    //let pathValOne = getRandomNumber(21, -10);
    //let pathValTwo = getRandomNumber(11, -20);
    //let pathDuration = getRandomNumber(1000, 1000);
    //console.log('ring ' + a);
    let pathValOne = maxValues[a];
    let pathValTwo = minValues[a];
    let pathDuration = 5000;

    let ringColor = getRingColor(a);

    for (let i = 1; i <= totalCircleElements; i++) {

      let currentRotation = 360 / totalCircleElements * i;
      let rotateContainer = document.createElement('a-entity');
      rotateContainer.setAttribute('rotation', `0 0 ${currentRotation}`);

      // generate circle element and set params
      let circleElementContainer = document.createElement('a-entity');
      circleElementContainer.setAttribute('position', `0 1 0`);
      let circleElement = document.createElement('a-entity');
      circleElement.setAttribute('class', `circleElement`);
      circleElement.setAttribute('scale', `${elementScale} ${elementScale} ${elementScale}`);
      circleElement.setAttribute('material', `color:#${ringColor}; metalness: 0; roughness: 0`);
      circleElement.setAttribute('geometry', `primitive: sphere; radius: 1.5`);
      circleElement.setAttribute('animation__yoyo', `property: scale; dir: alternate; dur: ${scaleDuration}; easing: easeInOutSine; loop: true; to: 0 0 0`);
      circleElementContainer.appendChild(circleElement);
      rotateContainer.appendChild(circleElementContainer);

      // generate path and apply it
      let track1 = document.createElement('a-curve');
      track1.setAttribute('class', `track${a}`);
      scene.append(track1);
      let point1 = document.createElement('a-curve-point');
      point1.setAttribute('position', '0 0 0');
      track1.append(point1);
      let point2 = document.createElement('a-curve-point');
      point2.setAttribute('position', `${pathValOne} ${pathValTwo} ${pathValOne}`);
      track1.append(point2);
      let point3 = document.createElement('a-curve-point');
      point3.setAttribute('position', `${pathValTwo} ${pathValOne} ${pathValTwo}`);
      track1.append(point3);
      let point4 = document.createElement('a-curve-point');
      point4.setAttribute('position', '0 0 0');
      track1.append(point4);
      circleElement.setAttribute(`alongpath`, `curve: .track${a}; dur: ${pathDuration}; loop: true`);

      // append element to main container
      objectContainer.appendChild(rotateContainer);

    }

  }
  eegData = [];
  setTimeout(generateAllElements, 5000);

}

//generateAllElements()
//setInterval(checkHeight, 200);
