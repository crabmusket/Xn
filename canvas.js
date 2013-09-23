var arrangement = 0;
var shapes = {};
var offset = 0.05;

var move = 0;
var zoom = 0;
var mouseX;
var mouseY;

var width = 10;
var length = 10;
var levels = 15;
var seed = 450;
var sparsity = 1;

function resizeCanvas()
{
	$W.canvas.width = window.innerWidth;
	$W.canvas.height = window.innerHeight;
	$W.camera.aspectRatio = $W.canvas.width / $W.canvas.height;
	$W.GL.viewport(0, 0, $W.canvas.width, $W.canvas.height)
}

//radii x, y, z
function constructRectangle(x, y, z)
{
	return [
		// Front face
		-x, -z,  y,
		 x, -z,  y,
		 x,  z,  y,
		-x,  z,  y,
		// Back face
		-x, -z, -y,
		-x,  z, -y,
		 x,  z, -y,
		 x, -z, -y,
		// Top face
		-x,  z, -y,
		-x,  z,  y,
		 x,  z,  y,
		 x,  z, -y,
		// Bottom face
		-x, -z, -y,
		 x, -z, -y,
		 x, -z,  y,
		-x, -z,  y,
		// Right face
		 x, -z, -y,
		 x,  z, -y,
		 x,  z,  y,
		 x, -z,  y,
		// Left face
		-x, -z, -y,
		-x, -z,  y,
		-x,  z,  y,
		-x,  z, -y
	];
}

//coordinates x, y, z, radius r, offset o, direction d
function constructSquare(x, y, z, r, o, d)
{
	if(d == "S") return [
		// Front face
		x-r, -z-r, y+o,
		x+r, -z-r, y+o,
		x+r, -z+r, y+o,
		x-r, -z+r, y+o
	];
	else if(d == "N") return [
		// Back face
		x-r, -z-r, y-o,
		x-r, -z+r, y-o,
		x+r, -z+r, y-o,
		x+r, -z-r, y-o
	];
	else if(d == "U") return [
		// Top face
		x-r,  -z+o, y-r,
		x-r,  -z+o, y+r,
		x+r,  -z+o, y+r,
		x+r,  -z+o, y-r
	];
	else if(d == "D") return [
		// Bottom face
		x-r, -z-o, y-r,
		x+r, -z-o, y-r,
		x+r, -z-o, y+r,
		x-r, -z-o, y+r
	];
	else if(d == "E") return [
		// Right face
		x+o, -z-r, y-r,
		x+o, -z+r, y-r,
		x+o, -z+r, y+r,
		x+o, -z-r, y+r
	];
	else return [
		// Left face
		x-o, -z-r, y-r,
		x-o, -z-r, y+r,
		x-o, -z+r, y+r,
		x-o, -z+r, y-r
	];
}

function constructShape(data)
{
	// Basic rectangle shape
	var x = parseInt(data[1]);
	var y = parseInt(data[2]);
	var z = parseInt(data[3]);

	var vertices = constructRectangle(x/2 - offset, y/2 - offset, z/2 - offset);
	var colours = $W.util.genDummyArray([0.7+(Math.random()-0.5)/8, 0.0, 0.0], 24);
	var indices = $W.constants.unitCube.indices;

	// Add doors as aligned faces
	var numDoors = parseInt(data[4]);
	for(var i = 0; i < numDoors; i++)
	{
		var idx = 5 + 4 * i;
		var lx = parseInt(data[idx]) - x/2 +0.5;
		var ly = parseInt(data[idx + 1]) - y/2 +0.5;
		var lz = parseInt(data[idx + 2]) - z/2 +0.5;
		var l = vertices.length / 3;
		vertices = vertices.concat(
			constructSquare(lx, ly, lz, 0.4, 0.6, data[idx + 3]));
		colours = colours.concat($W.util.genDummyArray([0.0, 0.7, 0.0], 4));
		indices = indices.concat([l+0, l+1, l+2, l+0, l+2, l+3]);
	}

	return [
		{'width': x, 'length': y, 'levels': z},
		[['vertex', vertices],
		['color', colours],
		['wglu_elements', indices]]
	];
}

function createObjects(data)
{
	if(data.length > 0)
	{
		var lines = data.split("\n");
		var line = 0;
		// Construct hash map of RoomShapes
		var numShapes = parseInt(lines[line]);
		line++;
		for(var i = 0; i < numShapes; i++)
		{
			var tokens = lines[line + i].split(" ");
			shapes[tokens[0]] = constructShape(tokens);
		}
		line += numShapes;

		// Create Room objects
		var numRooms = parseInt(lines[line]);
		line++;
		for(var i = 0; i < numRooms; i++)
		{
			var tokens = lines[line + i].split(" ");

			var room = new $W.Object({
				type: $W.GL.TRIANGLES,
				data: shapes[tokens[0]][1]},
				$W.PICKABLE);

			var x = shapes[tokens[0]][0]['width']/2;
			var y = shapes[tokens[0]][0]['length']/2;
			var z = shapes[tokens[0]][0]['levels']/2;

			room.setPosition(parseInt(tokens[1]) - width/2 + x,
			               -(parseInt(tokens[3]) - levels/2 + z),
			                 parseInt(tokens[2]) - length/2 + y);
			arrangement.addChild(room);
		}
		line += numRooms;

		// Create corridor segments
		var numCorridors = parseInt(lines[line]);
		line++;
		for(var i = 0; i < numCorridors; i++)
		{
			var tokens = lines[line + i].split(" ");

			var cor = new $W.Object({
				type: $W.GL.TRIANGLES,
				data: [
					['vertex', constructSquare(0, 0, 0, 0.5, 0.5, "D")],
					['color', $W.util.genDummyArray(
						[0.0, 0.0, 0.7+(Math.random()-0.5)/8], 4)],
					['wglu_elements', [0, 1, 2, 0, 2, 3]]
				]},
				$W.PICKABLE);

			cor.setPosition(parseInt(tokens[0]) - width/2 + 0.5,
			              -(parseInt(tokens[2]) - levels/2 + 0.5),
			                parseInt(tokens[1]) - length/2 + 0.5);
			arrangement.addChild(cor);
		}
		line += numCorridors;

		if(isNaN(numShapes) || isNaN(numRooms) || isNaN(numCorridors))
		{
			$('#errormsg').html(data);
			$('#error').toggle();
		}
	}
	else
	{
		$('#errormsg').html("No data returned from Xn.");
		$('#error').toggle();
	}
	$('#loading').toggle();
}

function loadMap()
{
	$W.reset();
	if(!$W.initialize()) return;

	$W.GL.clearColor(1.0, 1.0, 1.0, 1.0);
	$W.camera.setPosition(0, levels*0.4, levels*0.75);
	$W.camera.setTarget(0, levels*0.4, 0);

	var arrangementShape = [
		['vertex', constructRectangle(width/2, length/2, levels/2)],
		['color', $W.util.genDummyArray([0.6, 0.6, 0.6],
		          $W.constants.unitCube.vertices.length/3)],
		['wglu_elements', [0, 1, 1, 2, 2, 3, 3, 0,
		                   4, 5, 5, 6, 6, 7, 7, 4,
		                   8, 9, 9, 10, 10, 11, 11, 8,
		                   12, 13, 13, 14, 14, 15, 15, 12,
		                   16, 17, 17, 18, 18, 19, 19, 16,
		                   20, 21, 21, 22, 22, 23, 23, 20
		                   ]]
	];

	arrangement = new $W.Object({
		type: $W.GL.LINES,
		data: arrangementShape},
		$W.PICKABLE | $W.RENDERABLE);
	arrangement.setPosition(0, 0, 0);

	$('#loading').toggle();

	$.get("Xn.cgi",
	      {x: width, y: length, z: levels,
	       seed: seed, sparsity: sparsity,
	       density: $('#density').val(),
	       offset: $('#offset').val(),
	      },
	      createObjects);

	$W.start();
}

function initCanvas()
{
	$(window).resize(resizeCanvas);
	resizeCanvas();
	mouse = function(event)
	{
		var dx = event.pageX - mouseX;
		var dy = event.pageY - mouseY;
		if(move)
		{
			var p = arrangement.rotation.elements[0];
			var t = arrangement.rotation.elements[1];
			var r = arrangement.rotation.elements[2];
			arrangement.setRotation(p - dx, t, r);

			var x = $W.camera.position.elements[0];
			var y = $W.camera.position.elements[1];
			var z = $W.camera.position.elements[2];
			$W.camera.setPosition(x, y + dy / 8, z);
			$W.camera.target = $W.camera.target.add([0, dy / 32, 0]);
		}
		if(zoom)
		{
			var x = $W.camera.position.elements[0];
			var y = $W.camera.position.elements[1];
			var z = $W.camera.position.elements[2];
			$W.camera.setPosition(x, y, z + dy / 8);
		}
		mouseX = event.pageX;
		mouseY = event.pageY;
	};
	var canvas = $('#canvas');
	canvas.mousedown(function(event)
	{
		switch(event.which)
		{
			case 1:
				move = 1;
			break;
			case 3:
				zoom = 1;
			break;
		}
		mouseX = event.pageX;
		mouseY = event.pageY;
		canvas.mousemove(mouse);
	});
	canvas.mouseup(function(event)
	{
		switch(event.which)
		{
			case 1:
				move = 0;
			break;
			case 3:
				zoom = 0;
			break;
		}
		canvas.unbind('mousemove');
	});
	canvas.bind('mousewheel', function(event, delta)
	{
		var x = $W.camera.position.elements[0];
		var y = $W.camera.position.elements[1];
		var z = $W.camera.position.elements[2];
		$W.camera.setPosition(x, y + delta / 2, z);
		$W.camera.target = $W.camera.target.add([0, delta / 2, 0]);
	});
}

function updateLinks()
{
	var query = "Xn.cgi?x=" + width +
	            "&y=" + length +
	            "&z=" + levels +
	            "&seed=" + seed +
	            "&sparsity=" + sparsity +
	            "&density=" + $('#density').val() +
	            "&offset=" + $('#offset').val();
	$('#listlink').attr('href', query);
	$('#asciilink').attr('href', query + "&output=ASCII");
}

function initMenus()
{
	$('div.dropdown').click(function()
	{
		$("#" + $(this).attr('target')).slideToggle('slow');
	});
	$('div.sidebar').toggle();
	$('#width').spinit({ height: 25, width: 200,
	                     min: 4, initValue: width, max: 100,
	                     callback: function(val){ width = val; updateLinks(); },
	                     mask: "Grid width"});
	$('#length').spinit({ height: 25, width: 200,
	                      min: 4, initValue: length, max: 100,
	                      callback: function(val){ length = val; updateLinks(); },
	                      mask: "Grid length"});
	$('#height').spinit({ height: 25, width: 200,
	                      min: 4, initValue: levels, max: 100,
	                      callback: function(val){ levels = val; updateLinks(); },
	                      mask: "Grid height"});
	$('#seed').spinit({ height: 25, width: 200,
	                    min: 0, initValue: seed, max: 999999999,
	                    callback: function(val){ seed = val; updateLinks(); },
	                    mask: "Random seed"});
	$('#sparsity').spinit({ height: 25, width: 200,
	                        min: 1, initValue: sparsity, max: 100,
	                        callback: function(val){ sparsity = val; updateLinks(); },
	                        mask: "Sparsity"});
	$('select').click(updateLinks);
	$('.message').toggle();
	updateLinks();
}

function start()
{
	initMenus();
	loadMap();
	initCanvas();
};
