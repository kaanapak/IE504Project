# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import random
import time
from collections import defaultdict

import pandas as pd
import math
from random import randrange
import copy

class Patient:


    def __init__(self,no,sp,x,y,distances,patient_count):
        self.no=no
        self.sp = sp
        self.np = self.calculate_np()
        self.x = x
        self.y = y
        self.distances=distances
        self.patient_count=patient_count
        self.is_assigned=False
        self.temp_lostcost=0
        self.temp_lostPoint=0
        self.temp_distancePoint=0
        self.temp_center=0
        self.left_time=(3-self.sp)
        self.left_short=3
        self.num_short=0
        self.received_service=False
        self.transferred_out=False
        self.is_candidate=False
        self.treatments=[]


    def PrintTreatments(self):
        for treatment in self.treatments:
            treatment.Print()

    def calculate_np(self,planing_horizon = 14):
        long_alpha = 3
        short_alpha = 2
        return (planing_horizon - (long_alpha - self.sp)) / short_alpha

    def distance_to_Patient(self,patient):
        return self.distances.iloc[patient.no]

    def distance_to_Center(self,center):
        return self.distances.iloc[self.patient_count+center.Instance_no]

    #def getTempDistancePoint(self,network,center):
        #return network.distancePointCalculator(self, center)
    def getTempDist(self):
        return self.temp_distancePoint

class Treatment:

    def __init__(self,patient,type,day):
        self.day=day
        self.patient=patient
        self.type=type
        self.duration=self.initialize_duration()
    def Print(self):
        print("Day ",self.day," Type ",self.type)

    def PrintWP(self):
        print(" Type ", self.type," Patient ",self.patient.no)


    def initialize_duration(self):
        if(self.type=="Short"):
            return 2
        elif(self.type=="Normal"):
            return 4

class Machine:

    def __init__(self,no):
        self.no=no
        self.schedule=self.initialize_schedule()
        self.short_duration=2
        self.normal_duration =4
        self.day_duration=8

    def Print(self):
        for d_index in range(0,14):
            print(" Day",d_index+1)
            for treatment in self.schedule[d_index]:
                treatment.PrintWP()



    def initialize_schedule(self):
        schedule=[]
        for i in range(0,14):
            schedule.append(list())
        return schedule

    def calculate_total_duration(self,day):
        total_duration=0
        for treatment in self.schedule[day-1]:
            total_duration+=treatment.duration
        return total_duration

    def add_Patient(self,patient,type,day):
        treatment=Treatment(patient,type,day)
        if(self.calculate_total_duration(day)+treatment.duration<=self.day_duration):
            self.schedule[day-1].append(treatment)
            patient.treatments.append(treatment)
            return True
        else:
            return False

class Center:

    def __init__(self,no,Instance_no,name,district,x,y,number_of_machines,distances,patient_count,ch0,severity):
            self.name=name
            self.no=no
            self.Instance_no=Instance_no
            self.district=district
            self.x = x
            self.y = y
            self.number_of_machines = number_of_machines
            self.ch0 = ch0
            self.severity = severity
            if self.severity == "İyimser":
                self.number_of_machines = self.ch0 // 2

            elif self.severity == "Orta":
                self.number_of_machines = self.ch0 // 2

            else:
                self.number_of_machines = self.ch0

            self.capacity = self.calculate_capacity()
            self.distances = distances
            self.patient_count = patient_count
            self.patient_In_Center=0
            self.is_Full=False
            self.remaining_capacity=self.capacity
            self.patients=[]
            self.machines=self.initialize_machines()
            self.count_received=0
            self.ratios=14*[None]

    def totalService(self):
        for day in range(1,15):
            total_short = 0
            total_normal = 0
            for machine in self.machines:
                for treatment in machine.schedule[day-1]:
                    if(treatment.type=="Short"):
                        total_short+=1
                    else:
                        total_normal+=1
            print(" Day ",day," Short ",total_short," Normal ",total_normal," Ratio short ",total_short/(total_short+total_normal))

    def PrintPatientTreatments(self):
        print("---- Printing Patients")
        for patient in self.patients:


            if(patient.transferred_out==False):
                print("Patient ", patient.no)
                patient.PrintTreatments()
                print("   ")

    def PrintMachineTreatments(self):
        print("---- Printing Machines")
        for machine in self.machines:
            print("Machine ", machine.no)
            machine.Print()
            print("   ")

    def Paste(self,Center):
        self.name = copy.deepcopy(Center.name)
        self.no = copy.deepcopy(Center.no)
        self.Instance_no = copy.deepcopy(Center.Instance_no)
        self.district = copy.deepcopy(Center.district)
        self.x = copy.deepcopy(Center.x)
        self.y = copy.deepcopy(Center.y)
        self.number_of_machines = copy.deepcopy(Center.number_of_machines)
        self.ch0 = copy.deepcopy(Center.ch0)
        self.capacity = copy.deepcopy(Center.capacity)
        self.distances = copy.deepcopy(Center.distances)
        self.patient_count = copy.deepcopy(Center.patient_count)
        self.patient_In_Center = copy.deepcopy(Center.patient_In_Center)
        self.is_Full = copy.deepcopy(Center.is_Full)
        self.remaining_capacity = copy.deepcopy(Center.capacity)
        self.patients = copy.deepcopy(Center.patients)
        self.machines = copy.deepcopy(Center.machines)
        self.count_received = copy.deepcopy(Center.count_received)
        self.ratios=copy.deepcopy(Center.ratios)

    def initialize_machines(self):
        list_machines=[]
        for i in range(0,self.number_of_machines):
            current_machine=Machine(i)
            list_machines.append(current_machine)
        return list_machines
    #Scheduling
    def assignPatient(self,patient,type,day):
        for machine in self.machines:
            if(machine.add_Patient(patient,type,day)):
                if(type=="Short"):
                  patient.num_short+=1
                  patient.left_short-=1
                  patient.received_service=True
                  patient.left_time=2
                else:
                    patient.received_service = True
                    patient.left_time = 3
                return True
        return False

    # Scheduling
    def run_scheduling(self):
        #self.solve_schedule(1,0)
        self.solve_schedule_alt()
        for patient in self.patients:
            if(patient.transferred_out==True):
                self.remove_patient(patient)
            else:
                self.count_received+=1

    def solve_schedule_alt(self):

        list_ratios=[]

        # for ratio_int in range(4, 9):
        #     ratio_1 = ratio_int / 10
        #     for ratio_int2 in range(4, 9):
        #         ratio_2 = ratio_int2 / 10
        #         for ratio_int3 in range(4, 9):
        #             ratio_3 = ratio_int3 / 10
        #             for ratio_int4 in range(4, 9):
        #                 ratio_4 = ratio_int4 / 10
        #                 for ratio_int5 in range(4, 9):
        #                     ratio_5 = ratio_int5 / 10
        #                     list_ratios.append([ratio_1,ratio_2,ratio_3,ratio_4,ratio_5])

        for ratio_int in range(0, 6):
            ratio_1 = ratio_int / 10
            for ratio_int2 in range(0, 6):
                ratio_2 = ratio_int2 / 10
                for ratio_int3 in range(0, 6):
                    ratio_3 = ratio_int3 / 10
                    list_ratios.append([ratio_1,ratio_2,ratio_3,ratio_1,ratio_2,ratio_3,ratio_1,ratio_2,ratio_3,ratio_1,ratio_2,ratio_3,ratio_1,ratio_2])


        # for ratio_int in range(0, 6):
        #     ratio_1 = ratio_int / 10
        #     for ratio_int2 in range(0, 6):
        #         ratio_2 = ratio_int2 / 10
        #         for ratio_int3 in range(0, 6):
        #             ratio_3 = ratio_int3 / 10
        #             for ratio_int4 in range(0, 6):
        #                 ratio_4 = ratio_int4 / 10
        #                 list_ratios.append([ratio_1,ratio_1,ratio_2,ratio_3,ratio_4,ratio_4])


        # min_sol=0
        min_sol = Center(1, 1, 1, 1, 1, 1, 1, 1, 1, 1,severity=self.severity)
        min_obj = 1000000
        min_ratio = 0
        count_transferredOut = 0
        for ratio_l in list_ratios:
            try_center = copy.deepcopy(self)
            try_center.solve_schedule_RREasy(ratio_l)
            if (try_center.scheduling_evaluate() < min_obj):
                # print("At day ",day, "with ratio ",start, "objective ",try_center.scheduling_evaluate())
                min_obj = try_center.scheduling_evaluate()
                # min_sol=try_center
                # min_sol.Paste(try_center)
                min_obj = try_center.scheduling_evaluate()
                min_sol = copy.deepcopy(try_center)
        self.Paste(min_sol)

    # Scheduling
    def solve_schedule(self,day,given_start):
      if(day!=1):
       for patient in self.patients:
          patient.left_time-=1
          if(patient.left_time<0):
              patient.transferred_out=True
              patient.received_service=False

      daily_short_capacity = self.number_of_machines * 4

      #min_sol=0
      min_sol=Center(1, 1, 1, 1, 1, 1, 1, 1, 1, 1)
      min_obj=1000000
      min_ratio=0
      count_transferredOut=0
      recursive_day=2 #This affects run time
      if(day<=recursive_day or day>=15-recursive_day):
          list_strategy = []
          for start_int in range(4,9):
               start = start_int/10
               list_strategy.append(start)
          #list_strategy.append(0.7)
      else:
          list_strategy=[given_start]
      for start in list_strategy:
          #r_short = start + ((-start / 15) * (day - 1))
          r_short=start
          num_short=int(r_short*daily_short_capacity)
          left_short_capacity= self.number_of_machines * 4
          #try_center=Center(1,1,1,1,1,1,1,1,1,1)
          #try_center.Paste(self)
          try_center=copy.deepcopy(self)
          num_normal=math.floor((daily_short_capacity-num_short)/2)
          while(2*num_normal+num_short<daily_short_capacity):
              num_short+=1
          total_patients=num_short+num_normal
          candidate_patients=try_center.findCandidates(total_patients)
          assigned_short=0
          candidate_num=0
          while(assigned_short<num_short and candidate_num<len(candidate_patients)and left_short_capacity>=1):
            current_patient=candidate_patients[candidate_num]
            assigned=False
            if(current_patient.left_short>0):
                if(try_center.assignPatient(current_patient,"Short",day)):
                   assigned_short+=1
                   left_short_capacity-=1
                   assigned=True
            if(assigned==False):
              try_center.assignPatient(current_patient, "Normal", day)

            candidate_num+=1

          while ( candidate_num < len(candidate_patients)):

              current_patient = candidate_patients[candidate_num]
              if  (try_center.assignPatient(current_patient, "Normal", day)):
                  left_short_capacity -= 2
              else:
                  if(try_center.assignPatient(current_patient, "Short", day)):
                      left_short_capacity -= 1

              candidate_num+=1

          try_iter=20

          #for evaluation
          #t_out=self.total_out()
          #print(self.total_out())
          #try_center.scheduling_evaluate()
          #print("IIII Tried at ", day, " ratio ", start, " result ", try_center.scheduling_evaluate_D(try_center), " min_obj was ",min_obj)
          if(day==14):
              for patient in try_center.patients:
                  if(patient.received_service==False):
                      patient.transferred_out=True

          else:

            try_center.solve_schedule(day+1,start)

          print("kkkkkk Tried at ",day,"previous ratio",try_center.ratios[day-1]," ratio ",start," result " ,try_center.scheduling_evaluate()," min_obj was ",min_obj)
          if(try_center.scheduling_evaluate()<min_obj):
              #print("At day ",day, "with ratio ",start, "objective ",try_center.scheduling_evaluate())
              min_obj=try_center.scheduling_evaluate()

              #min_sol=try_center
              #min_sol.Paste(try_center)
              min_sol=copy.deepcopy(try_center)
              min_sol.ratios[day - 1] = start
              min_ratio=start


      #min_sol.ratios[day-1]=min_ratio
      self.Paste(min_sol)

    def solve_schedule_RREasy(self,list_R):
        daily_short_capacity = self.number_of_machines * 4
        for day in range(1,15):
            if (day != 1):
                for patient in self.patients:
                    patient.left_time -= 1
                    if (patient.left_time < 0):
                        patient.transferred_out = True
                        patient.received_service = False

            # # ratio_1,ratio_1,ratio_2,ratio_3,ratio_4,ratio_4
            # if day < 4:
            #     start = list_R[day - 1]
            #
            # elif (day == 13):
            #     start = list_R[4]
            # elif (day == 14):
            #     start = list_R[5]
            # else:
            #     start = list_R[3]
            start=list_R[day-1]
            r_short = start
            num_short = int(r_short * daily_short_capacity)
            left_short_capacity = self.number_of_machines * 4
            # try_center=Center(1,1,1,1,1,1,1,1,1,1)
            # try_center.Paste(self)

            num_normal = math.floor((daily_short_capacity - num_short) / 2)
            while (2 * num_normal + num_short < daily_short_capacity):
                num_short += 1
            total_patients = num_short + num_normal
            candidate_patients = self.findCandidates(total_patients)
            assigned_short = 0
            candidate_num = 0
            while (assigned_short < num_short and candidate_num < len(candidate_patients) and left_short_capacity >= 1):
                current_patient = candidate_patients[candidate_num]
                assigned = False
                if (current_patient.left_short > 0):
                    if (self.assignPatient(current_patient, "Short", day)):
                        assigned_short += 1
                        left_short_capacity -= 1
                        assigned = True
                if (assigned == False):
                    self.assignPatient(current_patient, "Normal", day)

                candidate_num += 1

            while (candidate_num < len(candidate_patients)):

                current_patient = candidate_patients[candidate_num]
                if (self.assignPatient(current_patient, "Normal", day)):
                    left_short_capacity -= 2
                else:
                    if (self.assignPatient(current_patient, "Short", day)):
                        left_short_capacity -= 1

                candidate_num += 1

            try_iter = 20

            # for evaluation
            # t_out=self.total_out()
            # print(self.total_out())
            # try_center.scheduling_evaluate()
            # print("IIII Tried at ", day, " ratio ", start, " result ", try_center.scheduling_evaluate_D(try_center), " min_obj was ",min_obj)
            if (day == 14):
                for patient in self.patients:
                    if (patient.received_service == False):
                        patient.transferred_out = True

            self.ratios[day-1]=start

    def solve_schedule_notR(self, day,list_R,severity):
        if (day != 1):
            for patient in self.patients:
                patient.left_time -= 1
                if (patient.left_time < 0):
                    patient.transferred_out = True
                    patient.received_service = False

        daily_short_capacity = self.number_of_machines * 4

        # min_sol=0
        min_sol = Center(1, 1, 1, 1, 1, 1, 1, 1, 1, 1,severity = self.severity)
        min_obj = 1000000
        min_ratio = 0
        count_transferredOut = 0
        if(day<3):
           list_strategy=list_R[day-1]
        elif(day==13):
           list_strategy = list_R[3]
        elif (day == 14):
            list_strategy = list_R[4]
        else:
            list_strategy = list_R[2]



        for start in [list_strategy]:
            # r_short = start + ((-start / 15) * (day - 1))
            r_short = start
            num_short = int(r_short * daily_short_capacity)
            left_short_capacity = self.number_of_machines * 4
            # try_center=Center(1,1,1,1,1,1,1,1,1,1)
            # try_center.Paste(self)
            try_center = copy.deepcopy(self)
            num_normal = math.floor((daily_short_capacity - num_short) / 2)
            while (2 * num_normal + num_short < daily_short_capacity):
                num_short += 1
            total_patients = num_short + num_normal
            candidate_patients = try_center.findCandidates(total_patients)
            assigned_short = 0
            candidate_num = 0
            while (assigned_short < num_short and candidate_num < len(candidate_patients) and left_short_capacity >= 1):
                current_patient = candidate_patients[candidate_num]
                assigned = False
                if (current_patient.left_short > 0):
                    if (try_center.assignPatient(current_patient, "Short", day)):
                        assigned_short += 1
                        left_short_capacity -= 1
                        assigned = True
                if (assigned == False):
                    try_center.assignPatient(current_patient, "Normal", day)

                candidate_num += 1

            while (candidate_num < len(candidate_patients)):

                current_patient = candidate_patients[candidate_num]
                if (try_center.assignPatient(current_patient, "Normal", day)):
                    left_short_capacity -= 2
                else:
                    if (try_center.assignPatient(current_patient, "Short", day)):
                        left_short_capacity -= 1

                candidate_num += 1

            try_iter = 20

            # for evaluation
            # t_out=self.total_out()
            # print(self.total_out())
            # try_center.scheduling_evaluate()
            # print("IIII Tried at ", day, " ratio ", start, " result ", try_center.scheduling_evaluate_D(try_center), " min_obj was ",min_obj)
            if (day == 14):
                for patient in try_center.patients:
                    if (patient.received_service == False):
                        patient.transferred_out = True

            else:

                try_center.solve_schedule_notR(day + 1, list_R,self.severity)

            print("kkkkkk Tried at ", day, "previous ratio", try_center.ratios[day - 1], " ratio ", start, " result ",
                  try_center.scheduling_evaluate(), " min_obj was ", min_obj)
            if (try_center.scheduling_evaluate() < min_obj):
                # print("At day ",day, "with ratio ",start, "objective ",try_center.scheduling_evaluate())
                min_obj = try_center.scheduling_evaluate()

                # min_sol=try_center
                # min_sol.Paste(try_center)
                min_sol = copy.deepcopy(try_center)
                min_sol.ratios[day - 1] = start
                min_ratio = start

        # min_sol.ratios[day-1]=min_ratio
        self.Paste(min_sol)

    def scheduling_evaluate(self):
        total_patient=0
        count_transferredOut=0
        count_Short=0
        for patient in self.patients:
            total_patient += 1
            count_Short += patient.num_short
            if(patient.transferred_out):
                count_transferredOut += 1
        return count_transferredOut * 1 + count_Short * 10 * 0.00001

    def scheduling_evaluate_D(self,center):
        total_patient=0
        count_transferredOut=0
        count_Short=0
        for patient in center.patients:
            total_patient+=1
            if(patient.transferred_out):
                count_transferredOut+=1
            else:
                count_Short += patient.num_short
        return count_transferredOut*1+count_Short*10

    def total_out(self):
        count_transferredOut=0
        for patient in self.patients:
            if(patient.transferred_out):
                count_transferredOut+=1
        return count_transferredOut

    def total_short(self):
        count_Short = 0
        for patient in self.patients:
            count_Short += patient.num_short
        return count_Short


    #Scheduling
    def findCandidates(self,mum_patient):

        for i in range(0,len(self.patients)):
            self.patients[i].is_candidate=False

        daily_short_capacity = self.number_of_machines * 4
        patients_prim = list(filter(lambda x:( x.received_service == True and x.left_time==0 and x.transferred_out == False ), self.patients))
        patients_prim = sorted(patients_prim, key=lambda x: x.left_short, reverse=True)
        patients=list(filter(lambda x: x.transferred_out == False and x not in patients_prim, self.patients))
        sorted_patients = sorted(patients, key=lambda x: x.left_time, reverse=False)
        candidate_patients=sorted_patients[0:(daily_short_capacity-len(patients_prim)+3)]
        for patient in candidate_patients:
            patient.is_candidate=True
        #filtered = candidate_patients[0:int(mum_patient)]
        filtered_sorted= sorted(candidate_patients, key=lambda x: x.left_short, reverse=True)
        patients_prim.extend(filtered_sorted)
        return patients_prim


    # Assignment
    def addPatient(self,patient):
        patient.is_assigned=True
        self.patients.append(patient)
        self.remaining_capacity-=1
        self.patient_In_Center+=1
        if(self.remaining_capacity<1):
            self.is_Full=True

    # Assignment
    def remove_patient(self,patient):
        patient.is_assigned = False
        self.patients.remove(patient)
        self.remaining_capacity += 1
        self.patient_In_Center -=1
        self.is_Full = False

    # Assignment
    def distance_to_Patient(self,patient):
        return self.distances.iloc[int(patient.no)]

    # Assignment
    def distance_to_Center(self,center):
        return self.distances.iloc[self.patient_count+int(center.Instance_no)]

    # Assignment
    def calculate_capacity(self,planing_horizon = 14,L = 4):
        long_alpha = 3
        short_alpha = 2

        c = 1
        inequality_lhs = long_alpha * c + 1
        inequality_rhs_top = (planing_horizon - (long_alpha - 1)) * c
        inequality_rhs_bottom = (planing_horizon - (long_alpha - 1) - L * short_alpha)/long_alpha + L * 0.5
        inequality_rhs = inequality_rhs_top / inequality_rhs_bottom

        while not inequality_lhs <= inequality_rhs and c < 100:
            c += 1
            inequality_lhs = long_alpha * c + 1
            inequality_rhs_top = (planing_horizon - (long_alpha - 1)) * c
            inequality_rhs_bottom = ((planing_horizon - (long_alpha - 1) - L * short_alpha) / long_alpha) + (L * 0.5)
            inequality_rhs = inequality_rhs_top / inequality_rhs_bottom

        #capacity_at_day_0 = self.number_of_machines * 0.2 * (8 / 4)  #8 hours on a day assumed
        #capacity_at_day_* (Ch0) = num_of_machines * hours_in_a_day / length of a long session (4-hours)
        ch0 = self.ch0

        capacity = (long_alpha * c + 1) * math.floor(ch0 / c) + long_alpha * (ch0 % c)


        #capacity = self.number_of_machines * 3.5
        return capacity


class Network:
    def __init__(self,simulation_scope,total_patients):
        self.centers=[]
        self.patients=[]
        self.simulation_scope = simulation_scope

        self.center_count=0
        self.total_patients=total_patients
        self.patient_count=0
        self.assigned_patients=0

    def Print(self):
        total_patient=0;
        total_distance = 0
        for center in self.centers:
            total_patient+= len(center.patients)
            print("Center ",center.no," Name ",center.name," Number of Patients ",center.patient_In_Center,"Center Capacity:",center.capacity)
            current_patient_list=center.patients
            sp1Patient=0
            sp2Patient=0
            sp3Patient=0
            current_distance=0
            for patient in current_patient_list:
                if(patient.sp==1):
                    sp1Patient+=1
                if(patient.sp==2):
                    sp2Patient+=1
                if(patient.sp==3):
                    sp3Patient+=1

                current_distance += patient.distance_to_Center(center) * patient.np
            print("Number of sp1: ",sp1Patient," Number of sp2 ",sp2Patient, "Number of sp3 ",sp3Patient)
            print("Total Distance at center ",current_distance)
            print("------------")
            total_distance += current_distance

        print('*******')
        print('Total patients Assigned ',total_patient)
        print('Number of transferred out ',(self.patient_count - total_patient))
        print('Total distance ',total_distance)

    def objective_function(self):  # SEFA: UPDATE WITH VALUES OF BETA and SENDING A PATIENT OUTSIDE
        total_distance = 0

        for center in self.centers:
            for patient in center.patients:
                total_distance += patient.distance_to_Center(center)*patient.np
        return total_distance

    def final_objective_function(self,epsilon = 0.00001):

        objective_function = 0

        for center in self.centers:
            for patient in center.patients:
                if patient.transferred_out:
                    center.remove_patient(patient)
                    #patient.transferred_out = True
                else:
                    patient.distance_to_Center(center) * patient.np * epsilon
            objective_function += center.total_short() * 10 * epsilon

        for patient in self.patients:
            if not patient.is_assigned:
                objective_function += 1
        print(objective_function)

    def scheduleSolver(self):
        total_objective = 0
        for center in self.centers:
            center.run_scheduling()
            counts = [0, 0, 0, 0]
            for patient in center.patients:
                sp = patient.sp
                counts[int(sp)] += 1

            print("Center ",center.no," Assigned: ",center.patient_In_Center," Received service ",center.count_received,"Number Of Machines:",center.number_of_machines)
            print("Center Patient Sp values:" + str(counts) )
            print("ratios ",center.ratios)
            #center_result = center.scheduling_evaluate()
            #total_objective += center_result
            #print("Objective Value:",str(center_result))
            print(" ")
        #print("Total Objective is:", str(total_objective))

    def add_patient(self,patient):
        self.patients.append(patient)
        self.patient_count+=1

    def add_center(self,center):
        self.centers.append(center)
        self.center_count+=1

    def candidate_patients(self,center,coverage):
        patient_list=[]
        for patient in self.patients:
            if (patient.is_assigned == False) and (center.distance_to_Patient(patient) <= coverage):
                patient_list.append(patient)

        return patient_list

    def nearest_otherC(self, patient,Rcenter):
        min_distance = 10000
        min_center=0
        for center in self.centers:
            if ((center.is_Full == False) and (center.Instance_no == Rcenter.Instance_no)):
                if (patient.distance_to_Center(center) < min_distance):
                    min_distance = patient.distance_to_Center(center)
                    min_center = center
        return min_distance, min_center

    def nearest_center(self,patient):
        min_distance = 10000
        for center in self.centers:
            if (center.is_Full == False):
                if (patient.distance_to_Center(center) < min_distance):
                    min_distance = patient.distance_to_Center(center)
                    min_center = center
        return min_distance, min_center

    def lostCostCalculator(self, patient,center):
        patient.temp_lostcost = self.nearest_otherC(patient,center)[0] - patient.distance_to_Center(center)

    def lostPointCalculator(self, patient,center):
        self.lostCostCalculator(patient,center)
        patient.temp_lostPoint = patient.temp_lostcost * patient.np

    def distancePointCalculator(self, patient,center):
        if(patient.distance_to_Center(center)!=0):
            #patient.temp_distancePoint = 1 / patient.distance_to_Center(center)
            patient.temp_distancePoint = patient.np / patient.distance_to_Center(center)
        else:
            patient.temp_distancePoint =0

    def distance_calculator(self, patient,center): #Distance calculation (C1 and P1 Algorithms)
        if patient.distance_to_Center(center)!=0:
            patient.temp_distancePoint = 1 / patient.distance_to_Center(center)
            # patient.temp_distancePoint = patient.np / patient.distance_to_Center(center)
        else:
            patient.temp_distancePoint =0

    def c1_constructive_heuristics(self):
        pass

    def assign_patients_balanced_sp_improved(self):
        for center in self.centers:

            patient_list = self.distPointList(center, 6)  # sorted by: patient.np / patient.distance_to_Center(center)
            daily_capacity = center.number_of_machines * 2
            cap_list = [0, daily_capacity, daily_capacity, daily_capacity]

            for patient in patient_list:
                sp = patient.sp
                if cap_list[int(sp)] > 0 and not center.is_Full and not patient.is_assigned:
                    center.addPatient(patient)
                    cap_list[int(sp)] -= 1
                    self.assigned_patients += 1

        # KAAN'IN SP1 LERI BUYUK CENTERLARA DAGITMA FIKRI BURADA UYGULANABILIR
        for center in self.centers:
            patient_list = self.distPointList(center, 6)  # sorted by: patient.np / patient.distance_to_Center(center)

            for patient in patient_list:
                if patient.sp == 1 and not center.is_Full and not patient.is_assigned:
                    center.addPatient(patient)

    def scheduling_improvement(self):
        print("improvement started")
        unscheduled_patients = [patient for patient in self.patients if patient.is_assigned]

        sorted_sp_patients = sorted(unscheduled_patients, key=lambda x: x.sp, reverse=False)
        sorted_centers = sorted(self.centers, key=lambda x: max(x.ratios), reverse=True)
        non_improving_centers = []
        for center in sorted_centers:
            serviced_count_before_improvement = center.count_received
            for patient in sorted_sp_patients:
                center.addPatient(patient)
                print(f"Patient {patient.no} assigned to Center {center.no}")
                center.run_scheduling()
                print(center.scheduling_evaluate())
                if serviced_count_before_improvement < center.count_received:
                    print(f"Before {serviced_count_before_improvement},After {center.count_received}")
                    continue
                else:
                    break

    def distancePointCalculatorPatient(self,patient):
        min_distance,min_center = self.nearest_center(patient)
        #print(patient.np)
        patient.temp_distancePoint = 1 / (min_distance * patient.np)
        #patient.temp_distancePoint = (100*(patient.np-5))/ min_distance

        patient.temp_center=min_center

    def patientListSorted(self):
        for patient in self.patients:
            self.distancePointCalculatorPatient(patient)
        return sorted(self.patients, key=lambda x: x.temp_distancePoint, reverse=True)

    def lostPointList(self, center, coverage):
        patient_list = self.candidate_patients(center,coverage)
        for patient in patient_list:
            self.lostPointCalculator(patient,center)
        return sorted(patient_list, key=lambda x: x.temp_lostPoint, reverse=True)

    def distPointList(self, center, coverage):
        patient_list = self.candidate_patients(center,coverage)
        for patient in patient_list:
            self.distancePointCalculator(patient,center)
        #return sorted(patient_list, key=patient.temp_distancePoint,reverse=True)
        #return sorted(patient_list, key=Patient.getTempDist(Patient), reverse=True)
        return sorted(patient_list, key=lambda x: x.temp_distancePoint, reverse=True)

    def assign_patients_balanced_sp(self):
        for center in self.centers:

            patient_list = self.distPointList(center, 6) #sorted by: patient.np / patient.distance_to_Center(center)
            remaining_sorted_patients = patient_list.copy()
            for i in range(round(center.capacity)//1):
                if center.is_Full:
                    break
                for sp in range(1,4):
                    if center.is_Full:
                        break
                    for patient in remaining_sorted_patients:
                        if center.is_Full:
                            break
                        if patient.sp == sp and not patient.is_assigned:
                            remaining_sorted_patients.remove(patient)
                            center.addPatient(patient)
                            self.assigned_patients += 1
                            break

    def assignPatientsByDistPoint(self):
        patient_list = self.patientListSorted()
        print('----------------')
        print(len(patient_list))
        print('----------------')

        for patient in patient_list:
            min_center=patient.temp_center
            if(patient.distance_to_Center(min_center)<6 and min_center.is_Full==False):
                min_center.addPatient(patient)
                self.assigned_patients += 1

    def assignbyLostPoint(self):
        for center in self.centers:
            patient_list=self.lostPointList(center,6)
            range_s=min(int(center.capacity),len(patient_list)-1)
            for i in range(0,range_s):
                center.addPatient(patient_list[i])
                self.assigned_patients += 1

    def assignbyDistPoint(self):
        for center in self.centers:

            patient_list = self.distPointList(center, 6)
            range_s = min(int(center.capacity), len(patient_list))

            for i in range(0, range_s):
                center.addPatient(patient_list[i])
                self.assigned_patients+=1

    def simulated_annealing(self,initial_temperature,cooling_rate,epoch_length):
        T = initial_temperature
        iteration = 1
        incumbent_solution = copy.deepcopy(network)
        while T > 0.01:
            min_delta = 1000

            for epoch in range(1,epoch_length+1):

                # Pick 2 random centers
                center_1 = random.choice(self.centers)
                center_2 = random.choice(self.centers)
                while center_1 == center_2:
                    center_2 = random.choice(self.centers)

                # Pick 2 random patients from these centers
                first_patient = random.choice(center_1.patients)
                second_patient = random.choice(center_2.patients)

                old_cost = center_1.distance_to_Patient(first_patient)*first_patient.np + center_2.distance_to_Patient(second_patient)*second_patient.np
                new_cost = center_1.distance_to_Patient(second_patient)*second_patient.np  + center_2.distance_to_Patient(first_patient)*first_patient.np
                delta = new_cost - old_cost

                if delta < min_delta:
                    min_delta = delta
                    min_center_1 = center_1
                    min_center_2 = center_2
                    min_patient_1 = first_patient
                    min_patient_2 = second_patient

            # If total distance reduces with this swap, Swap patients or accept according to metropolis criterion
            if min_delta < 0 or self.metropolis_criterion(min_delta,T):
                min_center_1.remove_patient(min_patient_1)
                min_center_2.remove_patient(min_patient_2)
                min_center_2.addPatient(min_patient_1)
                min_center_1.addPatient(min_patient_2)

                #print(f"Temperature = {T:.3f}: Solution accepted with {min_delta}")
                #break  # Should we stop epochs when we found an improving solution?

            else:
                pass
                #print(f"Temperature = {T:.3f} :Solution rejected with {min_delta}")

            if network.objective_function() < incumbent_solution.objective_function():
                incumbent_solution = copy.deepcopy(network)

            T *= cooling_rate

        return incumbent_solution

    def metropolis_criterion(self,delta,T):
        random_number = random.random()
        criteria = math.exp(-delta/T)
        return random_number < criteria


if __name__ == '__main__':
    dialysis_centers = pd.read_csv(r"dialysis_centers.csv",sep = ';')
    patient_coordinates=pd.read_csv(r"Koordinatlar.csv",sep = ';')
    patient_count=patient_coordinates.shape[0]
    distanceMatrix = pd.read_csv(r"UzaklıkMatris.csv", sep=';')
    network = Network(14,patient_count)
    #current_row=distanceMatrix.iloc[0]
    for index, row in patient_coordinates.iterrows():
        current_patient=Patient(row['Hasta No'],row['Sp'], row['Koordinat x'], row['Koordinat y'],distanceMatrix.iloc[int(row['Hasta No'])],patient_count)
        network.add_patient(current_patient)

    facility_instance=patient_coordinates.drop_duplicates(['Merkez/Hastane No'])
    facility_instance['Is_Instance']='Yes'
    #print(facility_instance)
    dialysis_centers = dialysis_centers.merge(facility_instance, how="left",on=['Merkez/Hastane No'])
    dialysis_centers=dialysis_centers[dialysis_centers['Is_Instance']=='Yes']

    center_instance_no=0
    distance_centers=distanceMatrix.tail(distanceMatrix.shape[0] -patient_count)
    ch0_data = pd.read_excel('Capacity.xlsx',sheet_name='B3')
    center_index = 0
    severity = "Karamsar"
    for index, row in dialysis_centers.iterrows():
        ch0 = ch0_data[severity].iloc[center_index]
        current_center = Center(row['Merkez/Hastane No'],center_instance_no,row['Diyaliz merkezi'],row['İlçe'], row['Koordinat x_x'], row['Koordinat y_x'],  row['Makineler'],distance_centers.iloc[center_instance_no],patient_count,ch0=ch0,severity=severity)
        center_instance_no += 1
        network.add_center(current_center)
        center_index += 1
# --------------------------
    network2 = copy.deepcopy(network)
    network3 = copy.deepcopy(network)
    network4 = copy.deepcopy(network)
    start = time.time()
    print('Patient Assignment')
    network.assign_patients_balanced_sp_improved() #distPoint
    network.Print()
    print(20 * "-")

    network.scheduleSolver()
    network.final_objective_function()
    end = time.time()
    print(f"Assignment and Scheduling Completed in {str(end - start)} seconds")

    network.scheduling_improvement()
    network.final_objective_function()

#    print(selectedCenter.scheduling_evaluate())

    # print("*****")
    #
    # center=Center(1, 1, "K", "district", 1, 1, 3, 1, 20, 10)
    # patient_no=0
    # for i in range (0,2):
    #     for s in range(1,4):
    #        patient=Patient(patient_no,s,1,1,1,10)
    #        patient_no+=1
    #        center.addPatient(patient)
    # center.run_scheduling()
    # print("Result ",center.scheduling_evaluate())
    # print("# of Out ",center.total_out())
    # center.PrintPatientTreatments()
    # center.PrintMachineTreatments()
    #center.totalService()
    #print('Lost Point Assignment')
    #network2.assignbyLostPoint()
    #network2.Print()
    # print(20 * "-")
    #
    # print('Dist Point Assignment')
    # #network3.assignbyDistPoint()
    # #network3.Print()
    # print(20 * "-")
    #
    # print("Balanced sp")
    # network4.assign_patients_balanced_sp()
    # network4.Print()
    #
    # print(20*"-")
    # print('Simulated Annealing Approach')
    #
    # simulated_annealing_results = []
    #
    # for iteration in range(0,10):
    #     start = time.time()
    #     improved_network = copy.deepcopy(network4)
    #     best_solution = improved_network.simulated_annealing(initial_temperature=100000,cooling_rate=0.8,epoch_length=10)
    #     end = time.time()
    #     simulated_annealing_results.append([iteration, best_solution.objective_function(), end - start])
    #
    # simulated_annealing_result_df = pd.DataFrame(simulated_annealing_results,columns=['Run','Objective Value','Runtime'])
    # print(simulated_annealing_result_df)
    # y = 5

