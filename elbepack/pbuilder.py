
import os
import urllib2



def pbuilder_ensure_chroot (builddir):
    pass


def pbuilder_write_config (builddir, xml, log):
    pbuilderrc_fname = os.path.join (builddir, "pbuilderrc")
    fp = open (pbuilderrc_fname, "w")

    fp.write ('#!/bin/sh\n')
    fp.write ('set -e\n')
    fp.write ('MIRRORSITE="%s"\n' % xml.get_primary_mirror(False))
    fp.write ('BASETGZ="%s"\n' % os.path.join (builddir, 'pbuilder', 'base.tgz'))

    fp.write ('DISTRIBUTION="%s"\n' % xml.prj.text ('suite'))

    fp.write ('BUILDRESULT="%s"\n' % os.path.join (builddir, 'pbuilder', 'result'))
    fp.write ('APTCACHE="%s"\n' % os.path.join (builddir, 'pbuilder', 'aptcache'))
    fp.write ('HOOKDIR="%s"\n' % os.path.join (builddir, 'pbuilder', 'hooks.d'))


    host_arch = log.get_command_out("dpkg --print-architecture").strip ()

    if xml.is_cross (host_arch):
        fp.write ('ARCHITECTURE="%s"\n' % xml.text ("project/buildimage/arch", key="arch"))
        fp.write ('DEBOOTSTRAP="qemu-debootstrap"\n')
        fp.write ('DEBOOTSTRAPOPTS=("${DEBOOTSTRAPOPTS[@]}" "--arch=$ARCHITECTURE")\n')


    fp.close()


def pbuilder_write_repo_hook (builddir, xml):

    pbuilder_hook_dir = os.path.join (builddir, "pbuilder", "hooks.d")

    fp = open (os.path.join (pbuilder_hook_dir, "D10elbe_apt_sources"), "w")

    if xml.prj is None:
        return "# No Project"

    if not xml.prj.has("mirror") and not xml.prj.has("mirror/cdrom"):
        return "# no mirrors configured"

    mirror = "#!/bin/sh\n"
    if xml.prj.has("mirror/primary_host"):
        mirror += 'echo "deb ' + xml.get_primary_mirror (None) + ' ' + xml.prj.text("suite") + ' main" >> /etc/apt/sources.list\n'

        if xml.prj.has("mirror/url-list"):
            for url in xml.prj.node("mirror/url-list"):
                if url.has("binary"):
                    mirror += 'echo "deb ' + url.text("binary").strip() + '" >> /etc/apt/sources.list\n'
                if url.has("key"):
                    key_url = url.text("key").strip()
                    key_url = key_url.replace("LOCALMACHINE", "10.0.2.2")
                    key_conn = urllib2.urlopen( key_url )
                    key_text = key_conn.read()
                    key_conn.close()

                    mirror += "cat << EOF | apt-key add -\n"
                    mirror += key_text + "\n"
                    mirror += "EOF\n"


    if xml.prj.has("mirror/cdrom"):
        mirror += 'echo "deb copy:///cdrom %s main added" >> /etc/apt/sources.list' % (xml.prj.text("suite"))

    mirror += 'apt-get update\n'
    mirror = mirror.replace("LOCALMACHINE", "10.0.2.2")

    fp.write (mirror)
    fp.close()

