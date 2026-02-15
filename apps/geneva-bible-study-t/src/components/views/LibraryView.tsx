import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { bibleBooks } from '@/lib/data'
import type { BookCategory } from '@/lib/types'

const categoryLabels: Record<BookCategory, string> = {
  law: 'The Law (Torah)',
  history: 'Historical Books',
  wisdom: 'Wisdom Literature',
  prophets: 'Prophets',
  gospels: 'The Gospels',
  epistles: 'Letters (Epistles)',
  apocalypse: 'Apocalyptic Literature',
  deuterocanon: 'Deuterocanonical Books',
  other: 'Other Writings'
}

const categoryDescriptions: Record<BookCategory, string> = {
  law: 'The first five books of Moses, foundational to Jewish and Christian faith',
  history: 'Chronicles of Israel\'s history from conquest to exile and restoration',
  wisdom: 'Poetry, proverbs, and philosophical reflections on life and faith',
  prophets: 'Messages from God through prophets calling Israel to faithfulness',
  gospels: 'Four accounts of Jesus\' life, teaching, death, and resurrection',
  epistles: 'Letters to early Christian communities addressing theology and practice',
  apocalypse: 'Visions of divine judgment and ultimate restoration',
  deuterocanon: 'Books included in Catholic and Orthodox canons, disputed by Protestants',
  other: 'Additional ancient Jewish and Christian writings'
}

export default function LibraryView() {
  const oldTestamentCategories: BookCategory[] = ['law', 'history', 'wisdom', 'prophets']
  const newTestamentCategories: BookCategory[] = ['gospels', 'epistles', 'apocalypse']
  const otherCategories: BookCategory[] = ['deuterocanon', 'other']

  const renderCategory = (category: BookCategory) => {
    const booksInCategory = bibleBooks.filter(book => book.category === category)
    if (booksInCategory.length === 0) return null

    return (
      <div key={category} className="mb-8">
        <h3 className="text-xl font-semibold mb-2 text-primary" style={{ fontFamily: 'var(--font-heading)' }}>
          {categoryLabels[category]}
        </h3>
        <p className="text-sm text-muted-foreground mb-4">
          {categoryDescriptions[category]}
        </p>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {booksInCategory.map(book => (
            <Card
              key={book.id}
              className="hover:shadow-lg hover:border-primary/50 transition-all cursor-pointer"
            >
              <CardHeader className="pb-3">
                <CardTitle className="text-lg">{book.title}</CardTitle>
                <CardDescription className="text-xs">
                  {book.chaptersCount} {book.chaptersCount === 1 ? 'chapter' : 'chapters'}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex flex-wrap gap-1">
                    <Badge variant="secondary" className="text-xs">
                      {book.metadata.testament.toUpperCase()}
                    </Badge>
                    {book.canonStatus.protestant === 'canonical' && (
                      <Badge variant="outline" className="text-xs">
                        Protestant
                      </Badge>
                    )}
                    {book.canonStatus.catholic === 'canonical' && (
                      <Badge variant="outline" className="text-xs">
                        Catholic
                      </Badge>
                    )}
                  </div>
                  {book.traditionalAuthor && (
                    <p className="text-xs text-muted-foreground">
                      Trad. author: {book.traditionalAuthor}
                    </p>
                  )}
                  <p className="text-xs text-muted-foreground">
                    {book.compositionDate}
                  </p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-8">
        <h2 className="text-3xl font-bold mb-2 text-foreground" style={{ fontFamily: 'var(--font-heading)' }}>
          The Bible as Library
        </h2>
        <p className="text-muted-foreground text-lg">
          A collection of sacred texts compiled across centuries and traditions
        </p>
      </div>

      <Card className="mb-8 bg-secondary/30 border-accent/30">
        <CardHeader>
          <CardTitle className="text-lg">Understanding the Canon</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Different Christian traditions include different books in their Bibles. The Protestant canon has 66 books,
            while Catholic and Orthodox traditions include additional books called the Deuterocanon or Apocrypha.
            Jewish scriptures (Tanakh) correspond roughly to the Protestant Old Testament but with different ordering.
            This library shows the canonical status of each book across traditions.
          </p>
        </CardContent>
      </Card>

      <div className="mb-8">
        <h3 className="text-2xl font-bold mb-4 text-primary" style={{ fontFamily: 'var(--font-heading)' }}>
          Old Testament
        </h3>
        <Separator className="mb-6" />
        {oldTestamentCategories.map(renderCategory)}
      </div>

      <div className="mb-8">
        <h3 className="text-2xl font-bold mb-4 text-primary" style={{ fontFamily: 'var(--font-heading)' }}>
          New Testament
        </h3>
        <Separator className="mb-6" />
        {newTestamentCategories.map(renderCategory)}
      </div>

      <div className="mb-8">
        <h3 className="text-2xl font-bold mb-4 text-primary" style={{ fontFamily: 'var(--font-heading)' }}>
          Additional Writings
        </h3>
        <Separator className="mb-6" />
        {otherCategories.map(renderCategory)}
        {bibleBooks.filter(b => otherCategories.includes(b.category)).length === 0 && (
          <Card>
            <CardContent className="pt-6 text-center text-muted-foreground">
              <p>Additional writings will be available in a future update.</p>
              <p className="text-sm mt-2">This includes deuterocanonical books and other ancient texts.</p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
