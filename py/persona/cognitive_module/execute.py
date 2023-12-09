


class Execute:

    @staticmethod
    def execute(persona, personas, plan):
        '''

        plan은 현재 plan의 act_address
        '''

        if "<random>" in plan and persona.scratch.planned_path == []:
            persona.scratch.act_path_set = False


        if not persona.scratch.act_path_set:
            # <target_tiles> is a list of tile coordinates where the persona may go
            # to execute the current action. The goal is to pick one of them.
            target_tiles = None

            print('aldhfoaf/????')
            print(plan)

            if "<persona>" in plan:
                persona.scratch.planned_path = "<persona>"
                pass

            elif "<waiting>" in plan:
                persona.scratch.planned_path = "<waiting>"
                pass

            elif "<random>" in plan:
                persona.scratch.planned_path = "<random>"
                pass

            else:
                persona.scratch.planned_path = "<object>"
                pass

            persona.scratch.act_path_set = True

        # ret = persona.scratch.planned_path
        #
        # description = f"{persona.scratch.act_description}"
        # description += f" @ {persona.scratch.act_address}"

        execution = {}
        execution["ret"] = persona.scratch.planned_path
        execution["description"] = persona.scratch.act_description
        execution["destination"] = persona.scratch.act_address

        # execution = ret, persona.scratch.act__pronunciatio, description
        return execution