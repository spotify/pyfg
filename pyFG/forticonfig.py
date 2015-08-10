import re
from collections import OrderedDict


class FortiConfig(object):
    def __init__(self, name='', config_type='', parent=None, vdom=None):
        """
        This object represents a block of config. For example::

            config system interface
                edit "port1"
                    set vdom "root"
                    set mode dhcp
                    set allowaccess ping
                    set type physical
                    set snmp-index 1
                next
            end


        It can contain parameters and sub_blocks.

        Args:
            * **name** (string) -- The path for the current block, for example *system interface*
            * **config_type** (string) -- The type of block, it can either be *config" or *edit*.
            * **parent** (string) -- If you are creating a subblock you can specify the parent block here.
            * **vdom** (string) -- If this block belongs to a vdom you have to specify it. This has to be specified\
                only in the root blocks. For example, on the 'system interface' block. You don't have to specify it\
                on the *port1* block.
        """
        self.name = name
        self.config_type = config_type
        self.parent = parent
        self.vdom = vdom
        self.paths = list()

        if config_type == 'edit':
            self.rel_path_fwd = 'edit %s\n' % name
            self.rel_path_bwd = 'next\n'
        elif config_type == 'config':
            self.rel_path_fwd = 'config %s\n' % name
            self.rel_path_bwd = 'end\n'

        if self.parent is None:
            self.rel_path_fwd = ''
            self.rel_path_bwd = ''
            self.full_path_fwd = self.rel_path_fwd
            self.full_path_bwd = self.rel_path_bwd
        else:
            self.full_path_fwd = '%s%s' % (self.get_parent().full_path_fwd, self.rel_path_fwd)
            self.full_path_bwd = '%s%s' % (self.rel_path_bwd, self.get_parent().full_path_bwd)

        self.sub_blocks = OrderedDict()
        self.new_sub_blocks = OrderedDict()
        self.parameters = dict()
        self.new_parameters = dict()

    def __repr__(self):
        return 'Config Block: %s' % self.get_name()

    def __str__(self):
        return '%s %s' % (self.config_type, self.name)

    def __getitem__(self, item):
        """
        By overriding this method we can access sub blocks of config easily. For example:

        config['router bgp']['neighbor']['10.1.1.1']

        """
        return self.sub_blocks[item]

    def __setitem__(self, key, value):
        """
        By overriding this method we can set sub blocks of config easily. For example:

        config['router bgp']['neighbor']['10.1.1.1'] = neighbor_sub_block
        """
        self.sub_blocks[key] = value
        value.set_parent(self)

    def get_name(self):
        """

        Returns:
            The name of the object.
        """
        return self.name

    def set_name(self, name):
        """
        Sets the name of the object.

        Args:
            * **name** (string) - The name you want for the object.
        """
        self.name = name

    def compare_config(self, target, init=True, indent_level=0):
        """
        This method will return all the necessary commands to get from the config we are in to the target
        config.

        Args:
            * **target** (:class:`~pyFG.forticonfig.FortiConfig`) - Target config.
            * **init** (bool) - This tells to the method if this is the first call to the method or if we are inside\
                                the recursion. You can ignore this parameter.
            * **indent_level** (int) - This tells the method how deep you are in the recursion. You can ignore it.

        Returns:
            A string containing all the necessary commands to reach the target config.
        """

        if init:
            fwd = self.full_path_fwd
            bwd = self.full_path_bwd
        else:
            fwd = self.rel_path_fwd
            bwd = self.rel_path_bwd

        indent = 4*indent_level*' '

        if indent_level == 0 and self.vdom is not None:
            if self.vdom == 'global':
                pre = 'conf global\n'
            else:
                pre = 'conf vdom\n  edit %s\n' % self.vdom
            post = 'end'
        else:
            pre = ''
            post = ''

        pre_block = '%s%s' % (indent, fwd)
        post_block = '%s%s' % (indent, bwd)

        my_params = self.parameters.keys()
        ot_params = target.parameters.keys()

        text = ''

        for param in my_params:
            if param not in ot_params:
                text += '  %sunset %s\n' % (indent, param)
            else:
                # We ignore quotes when comparing values
                if str(self.get_param(param)).replace('"', '') != str(target.get_param(param)).replace('"', ''):
                    text += '  %sset %s %s\n' % (indent, param, target.get_param(param))

        for param in ot_params:
            if param not in my_params:
                text += '  %sset %s %s\n' % (indent, param, target.get_param(param))

        my_blocks = self.sub_blocks.keys()
        ot_blocks = target.sub_blocks.keys()

        for block_name in my_blocks:
            if block_name not in ot_blocks:
                text += "    %sdelete %s\n" % (indent, block_name)
            else:
                text += self[block_name].compare_config(target[block_name], False, indent_level+1)

        for block_name in ot_blocks:
            if block_name not in my_blocks:
                text += target[block_name].to_text(True, indent_level+1, True)

        if text == '':
            return ''
        else:
            return '%s%s%s%s%s' % (pre, pre_block, text, post_block, post)

    def iterparams(self):
        """
        Allows you to iterate over the parameters of the block. For example:

        >>> conf = FortiConfig('router bgp')
        >>> conf.parse_config_output('here comes a srting with the config of a device')
        >>> for p_name, p_value in conf['router bgp']['neighbor']['172.20.213.23']:
        ...     print p_name, p_value
        remote_as 65101
        route-map-in "filter_inbound"
        route-map-out "filter_outbound"

        Yields:
            parameter_name, parameter_value
        """
        for key, value in self.parameters.iteritems():
            yield key, value

    def iterblocks(self):
        """
        Allows you to iterate over the sub_blocks of the block. For example:

        >>> conf = FortiConfig('router bgp')
        >>> conf.parse_config_output('here comes a srting with the config of a device')
        >>> for b_name, b_value in conf['router bgp']['neighbor'].iterblocks():
        ...     print b_name, b_value
        ...
        172.20.213.23 edit 172.20.213.23
        2.2.2.2 edit 2.2.2.2

        Yields:
            sub_block_name, sub_block_value
        """
        for key, data in self.sub_blocks.iteritems():
            yield key, data

    def get_parameter_names(self):
        """
        Returns:
            A list of strings. Each string is the name of a parameter for that block.
        """
        return self.parameters.keys()

    def get_block_names(self):
        """
        Returns:
            A list of strings. Each string is the name of a sub_block for that block.
        """
        return self.sub_blocks.keys()

    def set_parent(self, parent):
        """
        Args:
            - **parent** ((:class:`~pyFG.forticonfig.FortiConfig`): FortiConfig object you want to set as parent.
        """
        self.parent = parent

        if self.config_type == 'edit':
            self.rel_path_fwd = 'edit %s\n' % self.get_name()
            self.rel_path_bwd = 'next\n'
        elif self.config_type == 'config':
            self.rel_path_fwd = 'config %s\n' % self.get_name()
            self.rel_path_bwd = 'end\n'

        self.full_path_fwd = '%s%s' % (self.get_parent().full_path_fwd, self.rel_path_fwd)
        self.full_path_bwd = '%s%s' % (self.rel_path_bwd, self.get_parent().full_path_bwd)

    def get_parent(self):
        """
        Returns:
            (:class:`~pyFG.forticonfig.FortiConfig`) object that is assigned as parent
        """
        return self.parent

    def get_param(self, param):
        """
        Args:
            - **param** (string): Parameter name you want to get
        Returns:
            Parameter value
        """
        try:
            return self.parameters[param]
        except KeyError:
            return None

    def set_param(self, param, value):
        """
        When setting a parameter it is important that you don't forget the quotes if they are needed. For example,
        if you are setting a comment.

        Args:
            - **param** (string): Parameter name you want to set
            - **value** (string): Value you want to set
        """

        self.parameters[param] = str(value)

    def del_param(self, param):
        """
        Args:
            - **param** (string): Parameter name you want to delete
        """
        self.parameters.pop(param, None)

    def get_paths(self):
        """
        Returns:
            All the queries that were needed to get to this model of the config. This is useful in case
            you want to reload the running config.
        """
        if len(self.paths) > 0:
            return self.paths
        else:
            return self.get_block_names()

    def add_path(self, path):
        """
        Args:
            - **path** (string) - The path you want to set, for example 'system interfaces' or 'router bgp'.
        """
        self.paths.append(path)

    def del_block(self, block_name):
        """
        Args:
            - **block_name** (string): Sub_block name you want to delete
        """
        self.sub_blocks.pop(block_name, None)

    def to_text(self, relative=False, indent_level=0, clean_empty_block=False):
        """
        This method returns the object model in text format. You should be able to copy&paste this text into any
        device running a supported version of FortiOS.

        Args:
            - **relative** (bool):
                * If ``True``  the text returned will assume that you are one block away
                * If ``False`` the text returned will contain instructions to reach the block from the root.
            - **indent_level** (int): This value is for aesthetics only. It will help format the text in blocks to\
                increase readability.
            - **clean_empty_block** (bool):
                * If ``True`` a block without parameters or with sub_blocks without parameters will return an empty\
                    string
                * If ``False`` a block without parameters will still return how to create it.
        """
        if relative:
            fwd = self.rel_path_fwd
            bwd = self.rel_path_bwd
        else:
            fwd = self.full_path_fwd
            bwd = self.full_path_bwd

        indent = 4*indent_level*' '
        pre = '%s%s' % (indent, fwd)
        post = '%s%s' % (indent, bwd)

        text = ''
        for param, value in self.iterparams():
            text += '  %sset %s %s\n' % (indent, param, value)

        for key, block in self.iterblocks():
            text += block.to_text(True, indent_level+1)

        if len(text) > 0 or not clean_empty_block:
            text = '%s%s%s' % (pre, text, post)
        return text

    def parse_config_output(self, output):
        """
        This method will parse a string containing FortiOS config and will load it into the current
        :class:`~pyFG.forticonfig.FortiConfig` object.

        Args:
            - **output** (string) - A string containing a supported version of FortiOS config
        """
        regexp = re.compile('^(config |edit |set |end$|next$)(.*)')
        current_block = self

        if output.__class__ is str or output.__class__ is unicode:
            output = output.splitlines()

        for line in output:
            if 'uuid' in line:
                continue
            if 'snmp-index' in line:
                continue
            line = line.strip()
            result = regexp.match(line)

            if result is not None:
                action = result.group(1).strip()
                data = result.group(2).strip()


                if action == 'config' or action == 'edit':

                    data = data.replace('"', '')

                    if data not in current_block.get_block_names():
                        config_block = FortiConfig(data, action, current_block)
                        current_block[data] = config_block
                    else:
                        config_block = current_block[data]

                    current_block = config_block
                elif action == 'end' or action == 'next':
                    current_block = current_block.get_parent()
                elif action == 'set':
                    split_data = data.split(' ')
                    parameter = split_data[0]
                    data = split_data[1:]
                    current_block.set_param(parameter, ' '.join(data))
