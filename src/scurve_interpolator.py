import math
import matplotlib.pyplot as plt

class profile_segment:
    def __init__(self, t0, t, j, a, v, p):
        self.t0 = t0
        self.t = t
        self.j = j
        self.a = a
        self.v = v
        self.p = p

class Scurve_Interpolator:
    def __init__(self):
        self.segment = []
        self.max_jer = 255000
        self.max_vel = 500
        self.max_acc = 8000
        self.vel_start = 30
        self.vel_end = 10
        self.time_tick = 0.001

        self.p_target = 0
        self.t_target = 0
        self.v = 0
        self.p = 0
        self.a = 0
        self.j = 0
        self.t = 0

        for i in range(0, 7):
            self.segment.append(profile_segment(0, 0, 0, 0, 0, 0))

    def profile_seg_pos(self, seg, time = 0.0):
        return  seg.p + seg.v * time + 0.5 * seg.a * time * time + seg.j * time * time * time * (1 / 6)

    def profile_seg_vel(self, seg, time = 0.0):
        return seg.v + seg.a * time + 0.5 * seg.j * time * time

    def profile_seg_acc(self, seg, time = 0.0):
        return seg.a + seg.j * time

    def profile_seg_jrk(self, seg, time = 0.0):
        return seg.j

    ## Find the seg index for an S-Curve for "time".
    def profile_index(self, curve, time = 0.0):
        index = 0
        for index in range(1, 8):
            if index == 7:
                break
            if curve[index].t0 > time:
                break
        return index - 1

    ## Get the current position, velocity, acceleration or jerk
	## for an S-Curve at the given time.
    def profile_pos(self, curve, time = 0.0):
        i = self.profile_index(curve, time)
        return self.profile_seg_pos(curve[i], time - curve[i].t0)

    def profile_vel(self, curve, time = 0.0):
        i = self.profile_index(curve, time)
        return self.profile_seg_vel(curve[i], time - curve[i].t0)
        
    def profile_acc(self, curve, time = 0.0):
        i = self.profile_index(curve, time)
        return self.profile_seg_acc(curve[i], time - curve[i].t0)

    def profile_jrk(self, curve, time = 0.0):
        i = self.profile_index(curve, time)
        return self.profile_seg_jrk(curve[i], time - curve[i].t0)

    ## Connect the piecewise sections of an S-Curve together to
	## ensure a smooth graph.

    def calculate_profile(self):
        last_curve = self.segment[0]
        for i in range(1, 7):
            self.segment[i].t0 = last_curve.t0 + last_curve.t
            self.segment[i].a = self.profile_seg_acc(last_curve, last_curve.t)
            self.segment[i].v = self.profile_seg_vel(last_curve, last_curve.t)
            self.segment[i].p = self.profile_seg_pos(last_curve, last_curve.t)
            last_curve = self.segment[i]

    def recalculate_profile(self):
        t1 = 0.0
        t2 = 0.0
        t4 = 0.0
        t5 = 0.0

        self.segment[0] = profile_segment(0, 0, self.max_jer, 0, self.vel_start, 0)
        self.segment[1] = profile_segment(0, 0, 0, 0, 0, 0)
        self.segment[2] = profile_segment(0, 0, -self.max_jer, 0, 0, 0)
        self.segment[3] = profile_segment(0, 0, 0, 0, 0, 0)
        self.segment[4] = profile_segment(0, 0, -self.max_jer, 0, 0, 0)
        self.segment[5] = profile_segment(0, 0, 0, 0, 0, 0)
        self.segment[6] = profile_segment(0, 0, self.max_jer, 0, 0, 0)

        p = 0
        test_vel_min = max(self.vel_start, self.vel_end)
        test_vel_max = self.max_vel
        test_vel = test_vel_max
        while test_vel_max - test_vel_min > 1:
            if (self.max_acc * self.max_acc) / self.max_jer >= test_vel - self.vel_start:
                t1 = math.sqrt((test_vel - self.vel_start) / self.max_jer)
                t2 = 0
            else:
                t1 = self.max_acc / self.max_jer
                t2 = (test_vel - self.vel_start - self.max_acc * t1) / self.max_acc

            if (self.max_acc * self.max_acc) / self.max_jer >= test_vel - self.vel_end:
                t4 = math.sqrt((test_vel - self.vel_end) / self.max_jer)
                t5 = 0
            else:
                t4 = self.max_acc / self.max_jer
                t5 = (test_vel - self.vel_end - self.max_acc * t4) / self.max_acc

            self.segment[0].t = t1
            self.segment[2].t = t1
            self.segment[4].t = t4
            self.segment[6].t = t4
            self.segment[1].t = t2
            self.segment[5].t = t5

            self.calculate_profile()

            p = self.profile_pos(self.segment, self.segment[6].t0 + self.segment[6].t)

            if p > self.p_target:
                ## Need to reduce velocity
                test_vel_max = test_vel
                test_vel = (test_vel_max + test_vel_min) / 2.0
            else:
                if p > self.p_target - 0.1:
                    break
                else:
                    ## Increase velocity
                    test_vel_min = test_vel
                    test_vel = (test_vel_max + test_vel_min) / 2.0
        
        ## Adjust the constant velocity section to reach the target position
        t = (self.p_target - p) / test_vel
        self.segment[3].t = max(t, 0)
        self.calculate_profile()

    def start(self):
        self.recalculate_profile()
        self.p = 0
        self.v = 0
        self.a = 0
        self.j = 0
        self.t = 0
        self.t_target = self.segment[6].t0 + self.segment[6].t
    
    def stop(self):
        self.p = 0
        self.v = 0
        self.a = 0
        self.j = 0
        self.t = 0
        self.t_target = 0

    def update(self):
        self.t += self.time_tick

        if self.t > 0 and self.t <= self.segment[6].t0 + self.segment[6].t:
            self.v = self.profile_vel(self.segment, self.t)
            self.p = self.profile_pos(self.segment, self.t)
            self.a = self.profile_acc(self.segment, self.t)
            self.j = self.profile_jrk(self.segment, self.t)

        if self.p > self.p_target:
            self.p = self.p_target
            return True

        if self.t < self.segment[6].t0 + self.segment[6].t:
            return False

        self.v = self.profile_seg_vel(self.segment[6], self.segment[6].t)
        self.p = self.profile_seg_pos(self.segment[6], self.segment[6].t)
        self.a = self.profile_seg_acc(self.segment[6], self.segment[6].t)
        self.j = self.profile_seg_jrk(self.segment[6], self.segment[6].t)

        return True

    def set_moving_parameter(self, **parameter):
        for key, value in parameter.items():
            if key == 'a':
                self.max_acc = abs(value)
            if key == 'j':
                self.max_jer = abs(value)
            if key == 'v':
                self.max_vel = abs(value)
            if key == 'vs':
                self.vel_start = abs(value)
            if key == 've':
                self.vel_end = abs(value)

    def set_moving_distance(self, distance):
        self.p_target = abs(distance)

if __name__ == '__main__':
    test_a = Scurve_Interpolator()
    test_a.p_target = 200
    test_a.start()

    time_list = []
    j_list = []
    a_list = []
    v_list = []
    p_list = []

    while test_a.update() == False:
        time_list.append(test_a.t * 1000)
        j_list.append(test_a.j / 1000)
        a_list.append(test_a.a / 10)
        v_list.append(test_a.v)
        p_list.append(test_a.p)

    plt.title('S Curve')
    plt.plot(time_list, j_list, label = "j")
    plt.plot(time_list, a_list, label = "a")
    plt.plot(time_list, v_list, label = "v")
    plt.plot(time_list, p_list, label = "p")
    plt.xlabel('time (ms)')
    plt.ylabel('unit')
    plt.grid(linestyle = '--')
    plt.legend()
    plt.show() 
