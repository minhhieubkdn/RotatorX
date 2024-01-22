# X Rotator

## Dimensions

ROTATE_CENTER = [80, 61, -688]  
CAMERA_OFFSET = [-110, 0]

## G-CODE guides

### IsRotateX - Identify the COM port

```
>>> IsRotateX
<<< YesRotateX
```

### Position - Return Current Position

```
>>> Position
<<< 0.5
```

### M320 - Go to Home Position

```
>>> M320
<<< Ok
```

### M321 - Set Speed

```
>>> M321 50; set speed at 50mm/s
<<< Ok
```

### M322 - Set Position

```
>>> M322 100
<<< Ok
```

### M323 - Disable Stepper

```
>>> M323
<<< Ok
```

### M324 - Set Acceleration

```
>>> M324 5000; set accel 5000mm/s^2
<<< Ok
```

### M325 - Set Jerk

```
>>> M325 500000; set jerk 500000mm/s^3
<<< Ok
```

### M326 - Set Begin/Finish Velocity

```
>>> M326 2; set begin and finish vel 2mm/s
<<< Ok
```

### M327 - Set Home Position
```
>>> M327 -71.5; set home position at -71.5 and save to EEPROM
<<< Ok
```

### M328 - Load home position form EEPROM
```
>>> M328
<<< Ok
```